"""
CASSERISISSIMA 2.0 — Router: Dashboard KPIs
GET /api/v1/dashboard/kpis        — métricas clave del escenario activo
GET /api/v1/dashboard/sales-trend — tendencia de ventas últimas N semanas
GET /api/v1/dashboard/top-products — ranking de tortas más vendidas
"""
import logging
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import SaleTransaction, Product, Ingredient
from db.seed import get_active_scenario, SCENARIO_META

router = APIRouter()
logger = logging.getLogger(__name__)


def latest_sale_date(db: Session, scenario_id: int) -> date:
    """Ancla las ventanas temporales al último día con datos del escenario activo.

    Cae en date.today() si el escenario no tiene filas (escenario recién sembrado).
    """
    max_date = (
        db.query(func.max(SaleTransaction.sale_date))
        .filter(SaleTransaction.scenario_id == scenario_id)
        .scalar()
    )
    return max_date if max_date is not None else date.today()


@router.get("/dashboard/kpis")
def get_dashboard_kpis(db: Session = Depends(get_db)):
    """
    Métricas clave del mes actual vs mes anterior (filtradas por escenario activo).
    Retorna: ingresos, unidades vendidas, torta top, días de datos disponibles.
    """
    scenario_id = get_active_scenario(db)
    today = latest_sale_date(db, scenario_id)

    # Mes actual (desde el día 1)
    month_start = today.replace(day=1)
    # Mes anterior
    if today.month == 1:
        prev_month_start = date(today.year - 1, 12, 1)
        prev_month_end   = date(today.year, 1, 1) - timedelta(days=1)
    else:
        prev_month_start = date(today.year, today.month - 1, 1)
        prev_month_end   = month_start - timedelta(days=1)

    def _query_period(start: date, end: date):
        return (
            db.query(
                func.sum(SaleTransaction.quantity_sold).label("units"),
                func.sum(SaleTransaction.revenue).label("revenue"),
                func.count(func.distinct(SaleTransaction.sale_date)).label("days"),
            )
            .filter(
                SaleTransaction.scenario_id == scenario_id,
                SaleTransaction.sale_date >= start,
                SaleTransaction.sale_date <= end,
            )
            .first()
        )

    current  = _query_period(month_start, today)
    previous = _query_period(prev_month_start, prev_month_end)

    curr_revenue = float(current.revenue or 0)
    curr_units   = float(current.units or 0)
    prev_revenue = float(previous.revenue or 0)
    prev_units   = float(previous.units or 0)

    # Variaciones porcentuales
    def _pct_change(curr, prev):
        if prev == 0:
            return None
        return round((curr - prev) / prev * 100, 1)

    # Torta más vendida (mes actual)
    top = (
        db.query(Product.name, func.sum(SaleTransaction.quantity_sold).label("total"))
        .join(SaleTransaction, SaleTransaction.product_id == Product.id)
        .filter(
            SaleTransaction.scenario_id == scenario_id,
            SaleTransaction.sale_date >= month_start,
        )
        .group_by(Product.name)
        .order_by(desc("total"))
        .first()
    )

    # Total de días históricos disponibles en el escenario
    date_range = (
        db.query(
            func.min(SaleTransaction.sale_date).label("min_date"),
            func.max(SaleTransaction.sale_date).label("max_date"),
        )
        .filter(SaleTransaction.scenario_id == scenario_id)
        .first()
    )
    history_days = 0
    if date_range.min_date and date_range.max_date:
        history_days = (date_range.max_date - date_range.min_date).days + 1

    # Insumos en alerta crítica
    critical_ingredients = (
        db.query(func.count(Ingredient.id))
        .filter(Ingredient.current_stock <= Ingredient.alert_threshold)
        .scalar() or 0
    )

    meta = SCENARIO_META[scenario_id]

    return {
        "scenario": {
            "id":    scenario_id,
            "name":  meta["name"],
            "label": meta["label"],
            "color": meta["color"],
            "description": meta["description"],
        },
        "current_month": {
            "revenue": round(curr_revenue, 2),
            "units":   round(curr_units, 1),
            "days_with_data": int(current.days or 0),
        },
        "changes": {
            "revenue_pct": _pct_change(curr_revenue, prev_revenue),
            "units_pct":   _pct_change(curr_units, prev_units),
        },
        "top_product":           top.name if top else "—",
        "history_days":          history_days,
        "critical_ingredients":  int(critical_ingredients),
    }


@router.get("/dashboard/sales-trend")
def get_sales_trend(
    weeks: int = Query(default=8, ge=2, le=24),
    db: Session = Depends(get_db),
):
    """Tendencia de ventas semanales (ingresos + unidades) por las últimas N semanas."""
    scenario_id = get_active_scenario(db)
    today = latest_sale_date(db, scenario_id)
    start_date = today - timedelta(weeks=weeks)

    # Agrupar por semana ISO
    rows = (
        db.query(
            SaleTransaction.sale_date,
            func.sum(SaleTransaction.quantity_sold).label("units"),
            func.sum(SaleTransaction.revenue).label("revenue"),
        )
        .filter(
            SaleTransaction.scenario_id == scenario_id,
            SaleTransaction.sale_date >= start_date,
        )
        .group_by(SaleTransaction.sale_date)
        .order_by(SaleTransaction.sale_date)
        .all()
    )

    # Agrupar en semanas
    weekly: dict[str, dict] = {}
    for row in rows:
        d = row.sale_date
        week_key = f"{d.isocalendar().year}-W{d.isocalendar().week:02d}"
        if week_key not in weekly:
            weekly[week_key] = {"week": week_key, "units": 0.0, "revenue": 0.0, "days": 0}
        weekly[week_key]["units"]   += float(row.units or 0)
        weekly[week_key]["revenue"] += float(row.revenue or 0)
        weekly[week_key]["days"]    += 1

    trend = sorted(weekly.values(), key=lambda x: x["week"])
    for t in trend:
        t["units"]   = round(t["units"], 1)
        t["revenue"] = round(t["revenue"], 2)

    return {"scenario_id": scenario_id, "trend": trend}


@router.get("/dashboard/top-products")
def get_top_products(
    days: int = Query(default=30, ge=7, le=180),
    db: Session = Depends(get_db),
):
    """Ranking de tortas más vendidas en los últimos N días."""
    scenario_id = get_active_scenario(db)
    today = latest_sale_date(db, scenario_id)
    since = today - timedelta(days=days)

    rows = (
        db.query(
            Product.id,
            Product.name,
            Product.category,
            Product.selling_price,
            func.sum(SaleTransaction.quantity_sold).label("total_units"),
            func.sum(SaleTransaction.revenue).label("total_revenue"),
        )
        .join(SaleTransaction, SaleTransaction.product_id == Product.id)
        .filter(
            SaleTransaction.scenario_id == scenario_id,
            SaleTransaction.sale_date >= since,
        )
        .group_by(Product.id, Product.name, Product.category, Product.selling_price)
        .order_by(desc("total_units"))
        .all()
    )

    total_units = sum(float(r.total_units or 0) for r in rows)
    result = []
    for r in rows:
        units = float(r.total_units or 0)
        result.append({
            "id":           r.id,
            "name":         r.name,
            "category":     r.category,
            "price":        r.selling_price,
            "total_units":  round(units, 1),
            "total_revenue":round(float(r.total_revenue or 0), 2),
            "share_pct":    round(units / total_units * 100, 1) if total_units > 0 else 0,
        })

    return {"scenario_id": scenario_id, "days": days, "products": result}


@router.get("/dashboard/inventory")
def get_inventory_status(db: Session = Depends(get_db)):
    """Estado actual de los insumos con clasificación RAG (verde/amarillo/rojo)."""
    ingredients = db.query(Ingredient).order_by(Ingredient.name).all()
    items = []
    for ing in ingredients:
        ratio = ing.current_stock / ing.alert_threshold if ing.alert_threshold > 0 else 1.0
        if ing.current_stock <= ing.alert_threshold:
            status = "critical"
        elif ing.current_stock <= ing.alert_threshold * 1.5:
            status = "warning"
        else:
            status = "ok"

        items.append({
            "id":              ing.id,
            "name":            ing.name,
            "unit":            ing.unit,
            "current_stock":   round(ing.current_stock, 2),
            "alert_threshold": round(ing.alert_threshold, 2),
            "ratio":           round(ratio, 2),
            "status":          status,
        })

    critical_count = sum(1 for i in items if i["status"] == "critical")
    warning_count  = sum(1 for i in items if i["status"] == "warning")

    return {
        "ingredients":    items,
        "critical_count": critical_count,
        "warning_count":  warning_count,
        "total":          len(items),
    }
