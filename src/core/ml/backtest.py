"""
CASSERISISSIMA 2.0 — Walk-forward Backtesting (OE4)
Desliza una ventana deslizante sobre la historia sintética de cada producto y
pronostica los siguientes `horizon` días, avanzando 1 día por paso.

Diseño (satisface OE4 de la tesis):
  - Validación walk-forward deslizante (NO TimeSeriesSplit CV estático).
  - Reentrena el pipeline cada `retrain_every` días (default 7) para acotar
    costo; entre reentrenamientos reutiliza el último pipeline. Ver comentario
    más abajo.
  - Pronóstico multi-step recursivo: la predicción de t+h se alimenta como
    "demanda observada" para construir los lags de t+h+1 (estándar AR para TS).
  - Métricas MAE/MAPE/RMSE por ventana y agregadas.

NOTA sobre reutilización de modelos:
  `model_trainer.train_product_model` ejecuta RandomizedSearchCV + serializa un
  .joblib por llamada; eso es correcto para el modelo en producción pero
  prohibitivo en backtesting por-ventana (~cientos de reentrenamientos). Por eso
  reutilizamos directamente los mismos *builders* que él usa
  (`pipeline.build_pipeline`, `feature_engineering.build_features`,
  `pipeline.calculate_metrics`) con hiperparámetros fijos conservadores — los
  mismos del "Tier Medio" de model_trainer.py. No se inventa nuevo código de
  modelo.

Uso (desde src/):
    python -m core.ml.backtest            # smoke: 1 producto, ventana corta
    python -m core.ml.backtest --full     # reporte completo vía backtest_report
"""
import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from core.ml.feature_engineering import build_features, FEATURE_COLUMNS
from core.ml.pipeline import build_pipeline, calculate_metrics

logger = logging.getLogger(__name__)

# ── Defaults saneados para la tesis (escenario Óptimo, ~730 días) ──────────────
DEFAULT_TRAIN_WINDOW_DAYS = 180   # ~6 meses de historia por ventana
DEFAULT_HORIZON_DAYS = 14          # 2 semanas de pronóstico por paso
DEFAULT_RETRAIN_EVERY_DAYS = 7     # reentrenar 1x por semana (balance costo/precisión)
DEFAULT_STEP_DAYS = 1              # avance diario (walk-forward "puro")
DEFAULT_TAIL_DAYS = 90              # cola de historia para construir features del horizonte

# Hiperparámetros conservadores — idénticos al Tier Medio de model_trainer.py
_DEFAULT_RF = dict(n_estimators=200, max_depth=10, min_samples_leaf=5)

# Mínimo de filas-feature para entrenar (de model_trainer.MIN_ROWS_FOR_EWM=7)
MIN_ROWS_TO_TRAIN = 7


def _daily_series(sales_df: pd.DataFrame) -> pd.Series:
    """Reindexa la serie deventas a rango diario, rellena 0. Devuelve Series indexada por fecha."""
    df = sales_df.copy()
    df["sale_date"] = pd.to_datetime(df["sale_date"])
    df = df.sort_values("sale_date").drop_duplicates(subset="sale_date")
    df = df.set_index("sale_date")
    full = pd.date_range(df.index.min(), df.index.max(), freq="D")
    s = df["quantity_sold"].reindex(full).fillna(0.0).astype(float)
    s.index.name = "sale_date"
    return s


def _recursive_forecast(
    pipeline,
    history_tail: pd.Series,
    forecast_dates: list,
    shelf_life_days: int,
    tail_days: int = DEFAULT_TAIL_DAYS,
) -> list[float]:
    """
    Pronóstico multi-step recursivo.

    Para cada fecha futura `fd` construye features usando la cola de historia
    + las predicciones ya hechas (que actúan como "demanda observada" para los
    lags). Reutiliza `build_features` (sin reinventar ingeniería).

    La cola de `tail_days` basta para lag_28 y rolling_mean_21 (lag_365 usa el
    proxy EWM de build_features porque <365 días).
    """
    # Cola de historia real (no incluye días futuros)
    tail = history_tail.iloc[-tail_days:] if len(history_tail) > tail_days else history_tail
    hist_rows = list(zip(tail.index, tail.values))
    pred_qty: dict = {}
    yhats: list[float] = []

    for fd in forecast_dates:
        # Ensambla df: cola de historia + predicciones de días futuros < fd + fd (placeholder 0)
        rows = list(hist_rows)
        for fd2 in forecast_dates:
            if fd2 < fd:
                rows.append((fd2, pred_qty[fd2]))
        rows.append((fd, 0.0))  # placeholder; no afecta features de fd (lags usan shift)

        cur_df = pd.DataFrame(rows, columns=["sale_date", "quantity_sold"])
        feat = build_features(cur_df, external_factors=None,
                              shelf_life_days=shelf_life_days, apply_winsor=True)
        if feat.empty:
            # extremadamente improbable; fallback: media de historia
            yhat = float(history_tail.tail(7).mean())
        else:
            X = feat[FEATURE_COLUMNS]
            yhat = float(pipeline.predict(X.iloc[[-1]])[0])
        yhat = max(0.0, yhat)
        pred_qty[fd] = yhat
        yhats.append(yhat)

    return yhats


def walk_forward_backtest(
    sales_df: pd.DataFrame,
    product_id: str,
    sku: str,
    shelf_life_days: int,
    train_window_days: int = DEFAULT_TRAIN_WINDOW_DAYS,
    horizon: int = DEFAULT_HORIZON_DAYS,
    retrain_every: int = DEFAULT_RETRAIN_EVERY_DAYS,
    step: int = DEFAULT_STEP_DAYS,
    rf_params: dict | None = None,
    max_windows: int | None = None,
) -> dict:
    """
    Ejecuta walk-forward sliding backtest para un producto.

    Args:
        max_windows: si se setea, limita la cantidad de ventanas (útil para
            smoke tests rápidos). None = recorrer toda la historia disponible.

    Returns:
        dict con:
          - predictions: list[dict]     # {product_id, sku, date, window, y_pred, y_actual}
          - window_metrics: list[dict]  # {window, t_date, mae, mape, rmse}
          - aggregated: {mae, mape, rmse, n_windows, n_predictions}
          - config: parámetros efectivos usados
    """
    rf_params = {**_DEFAULT_RF, **(rf_params or {})}
    series = _daily_series(sales_df)
    n = len(series)
    dates = series.index

    # t = índice del último día de entrenamiento (0-based). Necesitamos >= train_window_days de historia.
    first_t = train_window_days - 1
    last_t = n - horizon - 1
    if last_t < first_t:
        raise ValueError(
            f"[{sku}] Historia insuficiente: {n} días < train_window({train_window_days}) + horizon({horizon})."
        )

    pipeline = None
    window_metrics: list[dict] = []
    predictions: list[dict] = []
    window_num = 0
    t_idx = first_t

    while t_idx <= last_t:
        if max_windows is not None and len(window_metrics) >= max_windows:
            break
        window_num += 1
        train_start = max(0, t_idx - train_window_days + 1)
        train_end = t_idx

        # ── Reentrenar? (cada `retrain_every` ventanas, o la primera) ──
        need_retrain = (pipeline is None) or (window_num == 1) or (((window_num - 1) % retrain_every) == 0)
        if need_retrain:
            train_dates = dates[train_start: train_end + 1]
            train_vals = series.iloc[train_start: train_end + 1]
            train_df = pd.DataFrame({
                "sale_date": train_dates,
                "quantity_sold": train_vals.values,
            })
            feat_train = build_features(train_df, None, shelf_life_days, apply_winsor=True)
            if len(feat_train) < MIN_ROWS_TO_TRAIN:
                t_idx += step
                continue
            X_train = feat_train[FEATURE_COLUMNS]
            y_train = feat_train["quantity_sold"]
            pipeline = build_pipeline(**rf_params)
            pipeline.fit(X_train, y_train)

        # ── Pronosticar horizonte ──
        history_tail = series.iloc[train_start: train_end + 1]
        forecast_dates = list(dates[train_end + 1: train_end + 1 + horizon])
        yhat_list = _recursive_forecast(pipeline, history_tail, forecast_dates, shelf_life_days)
        y_actual_list = [float(series.loc[fd]) for fd in forecast_dates]

        for fd, yhat, yact in zip(forecast_dates, yhat_list, y_actual_list):
            predictions.append({
                "product_id": product_id,
                "sku": sku,
                "date": fd.isoformat(),
                "window": window_num,
                "y_pred": round(yhat, 4),
                "y_actual": yact,
            })

        m = calculate_metrics(np.array(y_actual_list), np.array(yhat_list))
        window_metrics.append({
            "window": window_num,
            "t_date": dates[train_end].isoformat(),
            "mae": m["mae"],
            "mape": m["mape"],
            "rmse": m["rmse"],
        })

        t_idx += step

    # ── Agregados ──
    if predictions:
        all_pred = np.array([p["y_pred"] for p in predictions])
        all_act = np.array([p["y_actual"] for p in predictions])
        agg = calculate_metrics(all_act, all_pred)
        agg.update({
            "n_windows": window_num,
            "n_predictions": len(predictions),
        })
    else:
        agg = {"mae": None, "mape": None, "rmse": None, "n_windows": 0, "n_predictions": 0}

    return {
        "predictions": predictions,
        "window_metrics": window_metrics,
        "aggregated": agg,
        "config": {
            "train_window_days": train_window_days,
            "horizon": horizon,
            "retrain_every": retrain_every,
            "step": step,
            "shelf_life_days": shelf_life_days,
            "rf_params": rf_params,
        },
    }