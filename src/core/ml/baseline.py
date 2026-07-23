"""
CASSERISISSIMA 2.0 — Política Baseline (Pastelero Manual) — OE4
Implementa explícitamente la política "actual" del pastelero como regla simple
y parametrizable, para comparar contra la política del sistema.

Política baseline:
    producción(t) = media móvil de los últimos `k` días de demanda REAL
                    (disponible hasta t-1) multiplicada por (1 + buffer).

Es decir, el pastelero "mira los últimos k días" y produce un poco de más para
no quedarse sin stock. Es la heurística artesanal típica del rubro.

Parámetros por defecto saneados para la tesis (declarados y justificados):
    k = 7        (semana natural — coincide con el ciclo de compra del rubro)
    buffer = 0.10 (10% de sobreproducción; refleja aversión al stockout del pastelero)

Ambas políticas (baseline y sistema) deciden la producción del día t usando
SOLO información disponible hasta t-1 (comparación justa, walk-forward).
"""
import numpy as np
import pandas as pd

# ── Defaults declarados para la tesis ──────────────────────────────────────────
DEFAULT_BASELINE_K = 7
DEFAULT_BASELINE_BUFFER = 0.10   # 10% sobreproducción


def baseline_production(
    demand_series: pd.Series,
    k: int = DEFAULT_BASELINE_K,
    buffer: float = DEFAULT_BASELINE_BUFFER,
    round_production: bool = True,
) -> pd.Series:
    """
    Calcula la serie de producción baseline día a día.

    Producción(t) = rolling_mean(demand[t-k : t]) * (1 + buffer)
    Usando solo demanda hasta t-1 (shift(1) sobre la media móvil).

    El primer día no tiene historia → producción = demanda del día (o 0).
    En la práctica se rellena con el primer valor disponible.

    Args:
        demand_series: demanda real diaria (Series indexada por fecha).
        k: ventana de la media móvil.
        buffer: fracción de sobreproducción (0.10 = +10%).
        round_production: redondea a enteros (unidades discretas).

    Returns:
        Series de producción baseline, mismo índice que demand_series.
    """
    s = demand_series.astype(float).copy()
    # shift(1): la decisión de t usa demanda de [t-k-1 .. t-1]
    rolling = s.shift(1).rolling(window=k, min_periods=1).mean()
    # Faltantes iniciales → usar el primer valor disponible como proxy conservador
    first_valid = s.iloc[0] if len(s) > 0 else 0.0
    production = rolling.fillna(first_valid) * (1.0 + buffer)
    production = np.maximum(production, 0.0)
    if round_production:
        production = np.rint(production)
    production.name = "baseline_production"
    return production


def system_production(
    predictions_df: pd.DataFrame,
    demand_index: pd.DatetimeIndex,
    round_production: bool = True,
) -> pd.Series:
    """
    Construye la serie de producción del SISTEMA a partir de las predicciones
    walk-forward (una predicción y_actual_pred por fecha). Mapea a un índice diario.

    Args:
        predictions_df: DataFrame con columnas ['date','y_pred'] (salida de backtest).
        demand_index: índice de fechas diario sobre el que alinear.
        round_production: redondea a enteros.

    Returns:
        Series de producción del sistema alineada a demand_index.
    """
    if predictions_df.empty:
        return pd.Series(0.0, index=demand_index, name="system_production")

    df = predictions_df[["date", "y_pred"]].copy()
    df["date"] = pd.to_datetime(df["date"])
    # Si hay múltiples ventanas solapadas (horizon>1), tomar la predicción de la
    # ventana más reciente para cada fecha (la mejor información disponible).
    df = df.sort_values(["date", "window"] if "window" in df.columns else ["date"])
    df = df.drop_duplicates(subset="date", keep="last")
    df = df.set_index("date")["y_pred"].astype(float)

    prod = df.reindex(demand_index).fillna(0.0)
    prod = np.maximum(prod, 0.0)
    if round_production:
        prod = np.rint(prod)
    prod.name = "system_production"
    return prod


def compare_policies(
    predictions_df: pd.DataFrame,
    demand_series: pd.Series,
    shelf_life_days: int,
    baseline_k: int = DEFAULT_BASELINE_K,
    baseline_buffer: float = DEFAULT_BASELINE_BUFFER,
) -> dict:
    """
    Compara política baseline vs política del sistema en el mismo periodo.

    Returns:
        dict con:
          - system:   dict del simulador (waste_pct, fill_rate, totals, daily)
          - baseline: dict del simulador
          - comparison: {
                waste_pct_system, waste_pct_baseline, waste_reduction_pct,
                fill_rate_system, fill_rate_baseline, fill_rate_delta
            }
          - dates: índice de fechas usadas
    """
    from core.ml.spoilage import simulate_spoilage

    demand = demand_series.astype(float)
    demand = demand.reindex(demand.index).fillna(0.0)
    dates = list(demand.index)

    # Periodo común = fechas presentes en las predicciones
    if not predictions_df.empty:
        pred_dates = pd.to_datetime(predictions_df["date"]).unique()
        demand = demand.reindex(pd.to_datetime(demand.index))
        common_idx = demand.index.intersection(pred_dates)
        demand_period = demand.loc[common_idx]
    else:
        demand_period = demand

    dates_period = list(demand_period.index)

    # Producción del sistema y baseline en flotante: a 1-2 unidades/día, el
    # redondeo entero (np.rint) cuantiza a 0 la mayoría de las predicciones y
    # distorsiona la comparativa. Se mantiene la opción de redondeo para usos
    # puntuales, pero la comparación de merma se hace sobre cantidades float
    # (se promedian a lo largo del periodo).
    sys_prod = system_production(predictions_df, demand_period.index, round_production=False)
    base_prod = baseline_production(demand_period, k=baseline_k, buffer=baseline_buffer,
                                    round_production=False)

    sys_sim = simulate_spoilage(
        production=sys_prod.values, demand=demand_period.values,
        shelf_life_days=shelf_life_days, dates=dates_period, round_production=False,
    )
    base_sim = simulate_spoilage(
        production=base_prod.values, demand=demand_period.values,
        shelf_life_days=shelf_life_days, dates=dates_period, round_production=False,
    )

    w_sys = sys_sim["waste_pct"]
    w_base = base_sim["waste_pct"]
    waste_reduction_pct = ((w_base - w_sys) / w_base * 100.0) if w_base > 0 else 0.0

    fr_sys = sys_sim["fill_rate"]
    fr_base = base_sim["fill_rate"]

    return {
        "system": sys_sim,
        "baseline": base_sim,
        "comparison": {
            "waste_pct_system": round(w_sys, 6),
            "waste_pct_baseline": round(w_base, 6),
            "waste_reduction_pct": round(waste_reduction_pct, 4),
            "fill_rate_system": round(fr_sys, 6),
            "fill_rate_baseline": round(fr_base, 6),
            "fill_rate_delta": round(fr_sys - fr_base, 6),
        },
        "baseline_params": {"k": baseline_k, "buffer": baseline_buffer},
        "n_days": len(dates_period),
    }