"""
CASSERISISSIMA 2.0 — Router: Predicciones de Demanda
POST /api/v1/predict/{product_id}   — entrena modelo y genera pronóstico
GET  /api/v1/forecasts/{product_id} — pronóstico pre-calculado
GET  /api/v1/products               — lista de productos del catálogo
"""
import logging
import numpy as np
import pandas as pd
from datetime import date, timedelta, datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import desc

from db.database import get_db
from db.models import SaleTransaction, Product, DemandForecast
from db.seed import get_active_scenario, SCENARIO_META
from core.ml.feature_engineering import build_features, FEATURE_COLUMNS
from core.ml.model_trainer import train_product_model
from core.ml.model_registry import register_model, load_active_model
from core.ml.pipeline import predict_with_intervals
from core.operations_research.newsvendor import calculate_critical_ratio, newsvendor_optimal_quantity
from core.operations_research.reorder_point import calculate_reorder_point, evaluate_reorder_urgency

router = APIRouter()
logger = logging.getLogger(__name__)


class PredictRequest(BaseModel):
    horizon_days: int = 14
    service_level: float = 0.97
    force_retrain: bool = False


class ProductPriceUpdateRequest(BaseModel):
    selling_price: float = Field(..., gt=0.0)
    unit_cost: Optional[float] = Field(None, gt=0.0)


@router.get("/products")
def list_products(db: Session = Depends(get_db)):
    """Lista todos los productos activos del catálogo."""
    products = db.query(Product).filter(Product.is_active == True).order_by(Product.category, Product.name).all()
    return {
        "products": [
            {
                "id":       p.id,
                "sku":      p.sku,
                "name":     p.name,
                "category": p.category,
                "price":    p.selling_price,
                "cost":     p.unit_cost,
            }
            for p in products
        ]
    }


@router.put("/products/{product_id}")
def update_product_price(product_id: str, req: ProductPriceUpdateRequest, db: Session = Depends(get_db)):
    """Actualiza el precio de venta y costo unitario de un producto en el catálogo."""
    prod = db.query(Product).filter(Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail=f"Producto {product_id} no encontrado.")
    
    prod.selling_price = req.selling_price
    if req.unit_cost is not None:
        prod.unit_cost = req.unit_cost
        
    db.commit()
    return {
        "status": "ok",
        "product_id": product_id,
        "price": prod.selling_price,
        "cost": prod.unit_cost
    }


@router.post("/predict/{product_id}")
def predict_demand(product_id: str, req: PredictRequest, db: Session = Depends(get_db)):
    """
    Genera pronóstico de demanda D+1 a D+horizon para un producto.
    Entrena (o reutiliza) el modelo RF sobre los datos del escenario activo.
    """
    scenario_id = get_active_scenario(db)
    scenario_meta = SCENARIO_META[scenario_id]

    # 1. Cargar producto
    prod = db.query(Product).filter(Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail=f"Producto {product_id} no encontrado.")

    # 2. Cargar historial del escenario activo
    sales_rows = (
        db.query(SaleTransaction.sale_date, SaleTransaction.quantity_sold)
        .filter(
            SaleTransaction.scenario_id == scenario_id,
            SaleTransaction.product_id == product_id,
        )
        .order_by(SaleTransaction.sale_date)
        .all()
    )

    if len(sales_rows) < 7:
        raise HTTPException(
            status_code=422,
            detail=f"Datos insuficientes para pronosticar ({len(sales_rows)} días). Mínimo 7."
        )

    sales_df = pd.DataFrame(
        [(r.sale_date.isoformat(), float(r.quantity_sold)) for r in sales_rows],
        columns=["sale_date", "quantity_sold"]
    )

    # 3. Intentar cargar modelo activo (si no hay o se fuerza reentrenamiento)
    model_result = None
    if not req.force_retrain:
        model_result = load_active_model(product_id, db)

    # 4. Entrenar si es necesario
    if model_result is None:
        try:
            train_result = train_product_model(
                sales_df=sales_df,
                product_id=product_id,
                sku=prod.sku,
                shelf_life_days=prod.shelf_life_days,
                n_cv_splits=3,
            )
            reg_id = register_model(train_result, db)
            model_result = load_active_model(product_id, db)
            logger.info(f"[Predict] Modelo entrenado para {prod.sku} en escenario {scenario_id}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al entrenar: {str(e)}")

    pipeline, registry = model_result

    # 5. Construir features futuras (recursivo: lag_1 se actualiza con predicción previa)
    df_feat = build_features(sales_df, None, prod.shelf_life_days)
    last_date = pd.to_datetime(df_feat["sale_date"].max())
    future_dates = [last_date + timedelta(days=i + 1) for i in range(req.horizon_days)]

    # Buffer de valores recientes (históricos + predicciones que se van agregando)
    recent_buffer = list(df_feat["quantity_sold"].values[-365:])  # hasta 365 para lag_365

    future_rows = []
    for i, d in enumerate(future_dates):
        buf = recent_buffer  # referencia al buffer actualizado
        n = len(buf)

        # Lags: usan el buffer que incluye predicciones anteriores
        lag_1  = float(buf[-1])  if n >= 1  else 0.0
        lag_3  = float(buf[-3])  if n >= 3  else float(np.mean(buf[-min(3, n):]))
        lag_7  = float(buf[-7])  if n >= 7  else float(np.mean(buf[-min(7, n):]))
        lag_14 = float(buf[-14]) if n >= 14 else float(np.mean(buf[-min(14, n):]))
        lag_21 = float(buf[-21]) if n >= 21 else float(np.mean(buf[-min(21, n):]))
        lag_28 = float(buf[-28]) if n >= 28 else float(np.mean(buf[-min(28, n):]))
        lag_365 = float(buf[-365]) if n >= 365 else float(np.mean(buf[-min(60, n):]))

        # Rolling stats sobre el buffer
        last_7  = buf[-7:]  if n >= 7  else buf
        last_14 = buf[-14:] if n >= 14 else buf
        last_21 = buf[-21:] if n >= 21 else buf
        rolling_mean_7  = float(np.mean(last_7))
        rolling_mean_14 = float(np.mean(last_14))
        rolling_mean_21 = float(np.mean(last_21))
        rolling_std_7   = float(np.std(last_7))  if len(last_7) > 1 else 0.0
        rolling_std_14  = float(np.std(last_14)) if len(last_14) > 1 else 0.0

        # EWM approximation
        ewm_7 = float(pd.Series(last_7).ewm(span=7, min_periods=1).mean().iloc[-1])

        # Trend
        trend_window = buf[-min(7, n):]
        trend_7d = float(np.polyfit(range(len(trend_window)), trend_window, 1)[0]) if len(trend_window) >= 2 else 0.0

        # Calendar
        dow = d.weekday()
        dom = d.day
        month_val = d.month
        is_weekend = int(dow >= 5)
        is_payday = int(dom in {14, 15, 28, 29, 30, 31})

        row = {
            "lag_1": lag_1, "lag_3": lag_3, "lag_7": lag_7,
            "lag_14": lag_14, "lag_21": lag_21, "lag_28": lag_28, "lag_365": lag_365,
            "rolling_mean_7": rolling_mean_7, "rolling_mean_14": rolling_mean_14,
            "rolling_mean_21": rolling_mean_21,
            "rolling_std_7": rolling_std_7, "rolling_std_14": rolling_std_14,
            "ewm_7": ewm_7,
            "trend_7d": trend_7d,
            "day_of_week": dow, "day_of_month": dom,
            "week_of_year": d.isocalendar().week, "month": month_val,
            "dow_sin": float(np.sin(2 * np.pi * dow / 7)),
            "dow_cos": float(np.cos(2 * np.pi * dow / 7)),
            "month_sin": float(np.sin(2 * np.pi * (month_val - 1) / 12)),
            "month_cos": float(np.cos(2 * np.pi * (month_val - 1) / 12)),
            "dom_sin": float(np.sin(2 * np.pi * (dom - 1) / 31)),
            "dom_cos": float(np.cos(2 * np.pi * (dom - 1) / 31)),
            "is_weekend": is_weekend,
            "is_holiday": 0,
            "days_to_next_holiday": 30,
            "is_payday": is_payday,
            "weekend_x_mean7": is_weekend * rolling_mean_7,
            "payday_x_mean7": is_payday * rolling_mean_7,
            "holiday_x_std7": 0.0,
            "promo_active": 0, "promo_discount": 0.0,
            "temperature_max": 28.0, "temperature_min": 18.0, "precipitation_mm": 0.0,
            "shelf_life_days": prod.shelf_life_days,
        }
        future_rows.append(row)

        # Predicción recursiva: predecir este día y agregar al buffer para el siguiente
        X_single = pd.DataFrame([row])[FEATURE_COLUMNS]
        pred_val = float(np.maximum(0, pipeline.predict(X_single))[0])
        # Si el modelo usó log-transform, invertir
        model_hp = registry.get("hyperparameters", "{}")
        if isinstance(model_hp, str):
            import json as _json
            try:
                hp = _json.loads(model_hp)
            except Exception:
                hp = {}
        else:
            hp = model_hp
        if hp.get("log_transform"):
            pred_val = float(np.expm1(pred_val))
            pred_val = max(0.0, pred_val)
        recent_buffer.append(pred_val)

    X_future = pd.DataFrame(future_rows)[FEATURE_COLUMNS]
    forecast_df = predict_with_intervals(pipeline, X_future, registry=registry)
    forecast_df["forecast_date"] = [d.date().isoformat() for d in future_dates]

    # 6. ROP y Newsvendor
    recent_std = float(sales_df["quantity_sold"].tail(30).std()) or 0.3
    avg_demand = float(forecast_df["predicted"].mean())
    mape = registry.get("mape_val", 0.20)
    rmse = registry.get("rmse_val", recent_std)

    cr = calculate_critical_ratio(prod.unit_cost, prod.selling_price)
    rop_result = calculate_reorder_point(
        avg_daily_demand=avg_demand,
        demand_std_daily=recent_std,
        lead_time_days=prod.lead_time_days,
        mape=mape,
        rmse=rmse,
        service_level=req.service_level,
    )
    newsvendor = newsvendor_optimal_quantity(
        mu_demand=avg_demand * prod.lead_time_days,
        sigma_demand=recent_std * (prod.lead_time_days ** 0.5),
        critical_ratio=cr,
    )

    # 7. Guardar pronósticos en DB
    for _, row in forecast_df.iterrows():
        existing = (
            db.query(DemandForecast)
            .filter(
                DemandForecast.product_id == product_id,
                DemandForecast.forecast_date == date.fromisoformat(row["forecast_date"]),
                DemandForecast.model_version == registry["version_tag"],
            )
            .first()
        )
        if existing:
            existing.predicted_demand = float(row["predicted"])
            existing.lower_bound_90   = float(row["lower"])
            existing.upper_bound_90   = float(row["upper"])
        else:
            db.add(DemandForecast(
                product_id=product_id,
                model_version=registry["version_tag"],
                forecast_date=date.fromisoformat(row["forecast_date"]),
                predicted_demand=float(row["predicted"]),
                lower_bound_90=float(row["lower"]),
                upper_bound_90=float(row["upper"]),
                mape=mape,
                rmse=rmse,
            ))
    db.commit()

    return {
        "product":      {"id": product_id, "sku": prod.sku, "name": prod.name},
        "scenario":     {"id": scenario_id, "name": scenario_meta["name"]},
        "model":        registry,
        "forecasts":    forecast_df.to_dict(orient="records"),
        "reorder": {
            "rop":           rop_result,
            "newsvendor":    newsvendor,
            "critical_ratio": round(cr, 4),
            "avg_daily_demand": round(avg_demand, 3),
        },
    }


@router.get("/forecasts/{product_id}")
def get_stored_forecasts(product_id: str, days: int = 14, db: Session = Depends(get_db)):
    """Recupera los últimos pronósticos almacenados para un producto."""
    today = date.today()
    rows = (
        db.query(DemandForecast)
        .filter(
            DemandForecast.product_id == product_id,
            DemandForecast.forecast_date >= today,
        )
        .order_by(DemandForecast.forecast_date)
        .limit(days)
        .all()
    )
    return {
        "product_id": product_id,
        "forecasts": [
            {
                "forecast_date":    r.forecast_date.isoformat(),
                "predicted_demand": round(r.predicted_demand, 2),
                "lower_bound_90":   round(r.lower_bound_90, 2),
                "upper_bound_90":   round(r.upper_bound_90, 2),
                "model_version":    r.model_version,
            }
            for r in rows
        ],
    }
