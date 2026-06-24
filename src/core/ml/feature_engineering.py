"""
CASSERISISSIMA 2.0 — Feature Engineering Pipeline v3 (Optimizado)
Transforma datos históricos de ventas en features para el modelo de pronóstico.

Mejoras sobre v2:
  - Lags adicionales: lag_3 (patrón viernes→lunes) y lag_28 (ciclo mensual)
  - Encoding cíclico (sin/cos) para day_of_week, month, day_of_month
  - Features de interacción: weekend×mean7, payday×mean7, holiday×std7
  - EWM(span=7) como feature de momentum reciente
  - Winsorización y lag_365 inteligente conservados de v2
"""
import logging

import numpy as np
import pandas as pd
from typing import Optional

logger = logging.getLogger(__name__)

FEATURE_COLUMNS = [
    # Lags
    "lag_1", "lag_3", "lag_7", "lag_14", "lag_21", "lag_28", "lag_365",
    # Rolling statistics
    "rolling_mean_7", "rolling_mean_14", "rolling_mean_21",
    "rolling_std_7", "rolling_std_14",
    # Momentum
    "ewm_7",
    # Trend
    "trend_7d",
    # Calendar (raw integers — backward compatible)
    "day_of_week", "day_of_month", "week_of_year", "month",
    # Calendar (cyclic encoding — new)
    "dow_sin", "dow_cos",
    "month_sin", "month_cos",
    "dom_sin", "dom_cos",
    # Binary calendar
    "is_weekend", "is_holiday", "days_to_next_holiday", "is_payday",
    # Interactions
    "weekend_x_mean7", "payday_x_mean7", "holiday_x_std7",
    # External factors
    "promo_active", "promo_discount",
    "temperature_max", "temperature_min", "precipitation_mm",
    # Product attribute
    "shelf_life_days",
]


def _winsorize(series: pd.Series, iqr_factor: float = 1.5) -> pd.Series:
    """
    Winsorización basada en IQR para controlar outliers extremos.
    No elimina filas: los valores atípicos se recortan al fence.
    Esencial para series de repostería artesanal donde un día de evento
    puede triplicar la venta habitual.
    """
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        # Evitar colapsar la serie a 0 si la gran mayoría de días no tienen ventas.
        # En su lugar, usamos el percentil 99 como límite superior.
        lower_fence = 0.0
        upper_fence = float(series.quantile(0.99))
    else:
        lower_fence = max(0.0, q1 - iqr_factor * iqr)  # la demanda nunca es negativa
        upper_fence = q3 + iqr_factor * iqr
    
    clipped = series.clip(lower=lower_fence, upper=upper_fence)
    n_clipped = int((series != clipped).sum())
    if n_clipped > 0:
        logger.debug(f"Winsorización: {n_clipped} valores recortados (IQR×{iqr_factor}). "
                     f"Fence: [{lower_fence:.2f}, {upper_fence:.2f}]")
    return clipped


def _smart_lag_365(qty_orig: pd.Series, date_index: pd.DatetimeIndex) -> pd.Series:
    """
    Lag anual inteligente:
      - Si hay ≥ 365 días de historia → lag real desplazado 365 días
      - Si hay < 365 días → EWM(span=60) como proxy de memoria larga
    Evita rellenar con la media global (demasiado informativa para fechas recientes).
    """
    if len(qty_orig) >= 365:
        lag = qty_orig.shift(365)
        # Rellenar NaN al inicio con EWM de los primeros registros disponibles
        ewm_fill = qty_orig.ewm(span=60, min_periods=5).mean()
        return lag.fillna(ewm_fill)
    else:
        logger.debug(f"Historia < 365 días ({len(qty_orig)} días): usando EWM(span=60) para lag_365")
        return qty_orig.ewm(span=60, min_periods=5).mean().shift(1)


def build_features(
    df: pd.DataFrame,
    external_factors: Optional[pd.DataFrame] = None,
    shelf_life_days: int = 3,
    apply_winsor: bool = True,
) -> pd.DataFrame:
    """
    Construye el conjunto completo de features a partir de una serie temporal
    de ventas de un producto.

    Args:
        df: DataFrame con columnas ['sale_date', 'quantity_sold'].
        external_factors: DataFrame opcional con factores externos.
        shelf_life_days: Vida útil del producto en días.
        apply_winsor: Si True, aplica Winsorización a quantity_sold.

    Returns:
        DataFrame con todas las features; filas con NaN eliminadas.
    """
    df = df.copy().sort_values("sale_date").reset_index(drop=True)
    df["sale_date"] = pd.to_datetime(df["sale_date"])
    df = df.set_index("sale_date")

    # Rellenar días sin venta
    full_idx = pd.date_range(df.index.min(), df.index.max(), freq="D")
    df = df.reindex(full_idx)
    df["quantity_sold"] = df["quantity_sold"].fillna(0)
    df.index.name = "sale_date"

    logger.info(f"[FeatureEng] Procesando {len(df)} días de historia.")

    # Control de outliers ANTES de calcular lags
    if apply_winsor:
        df["quantity_sold"] = _winsorize(df["quantity_sold"])

    qty = df["quantity_sold"]

    # ── Lag Features ─────────────────────────────────────────────────────────
    df["lag_1"]  = qty.shift(1)
    df["lag_3"]  = qty.shift(3)
    df["lag_7"]  = qty.shift(7)
    df["lag_14"] = qty.shift(14)
    df["lag_21"] = qty.shift(21)
    df["lag_28"] = qty.shift(28)
    df["lag_365"] = _smart_lag_365(qty, df.index)

    # ── Rolling Statistics ────────────────────────────────────────────────────
    qty_shifted = qty.shift(1)
    df["rolling_mean_7"]  = qty_shifted.rolling(7).mean()
    df["rolling_mean_14"] = qty_shifted.rolling(14).mean()
    df["rolling_mean_21"] = qty_shifted.rolling(21).mean()
    df["rolling_std_7"]   = qty_shifted.rolling(7).std().fillna(0)
    df["rolling_std_14"]  = qty_shifted.rolling(14).std().fillna(0)

    # ── EWM Momentum ─────────────────────────────────────────────────────────
    df["ewm_7"] = qty_shifted.ewm(span=7, min_periods=1).mean()

    # ── Tendencia lineal (pendiente últimos 7 días) ───────────────────────────
    def _linear_trend(series: pd.Series) -> float:
        if series.isna().any() or len(series) < 2:
            return 0.0
        x = np.arange(len(series))
        coef = np.polyfit(x, series.values, deg=1)
        return float(coef[0])

    df["trend_7d"] = (
        qty_shifted
        .rolling(7)
        .apply(_linear_trend, raw=False)
        .fillna(0)
    )

    # ── Variables Calendario (raw integers) ──────────────────────────────────
    df["day_of_week"]  = df.index.dayofweek.astype(int)
    df["day_of_month"] = df.index.day.astype(int)
    df["week_of_year"] = df.index.isocalendar().week.astype(int)
    df["month"]        = df.index.month.astype(int)
    df["is_weekend"]   = (df["day_of_week"] >= 5).astype(int)
    # Quincenas venezolanas: días 14-15 y 28-31
    df["is_payday"]    = df["day_of_month"].isin([14, 15, 28, 29, 30, 31]).astype(int)

    # ── Encoding Cíclico (sin/cos) ───────────────────────────────────────────
    df["dow_sin"]   = np.sin(2 * np.pi * df["day_of_week"] / 7)
    df["dow_cos"]   = np.cos(2 * np.pi * df["day_of_week"] / 7)
    df["month_sin"] = np.sin(2 * np.pi * (df["month"] - 1) / 12)
    df["month_cos"] = np.cos(2 * np.pi * (df["month"] - 1) / 12)
    df["dom_sin"]   = np.sin(2 * np.pi * (df["day_of_month"] - 1) / 31)
    df["dom_cos"]   = np.cos(2 * np.pi * (df["day_of_month"] - 1) / 31)

    # ── Factores Externos ────────────────────────────────────────────────────
    if external_factors is not None:
        ext = external_factors.copy()
        ext["factor_date"] = pd.to_datetime(ext["factor_date"])
        ext = ext.set_index("factor_date")

        df["is_holiday"]   = ext["is_holiday"].reindex(df.index).fillna(False).astype(int)
        df["promo_active"] = ext["promo_active"].reindex(df.index).fillna(False).astype(int)
        df["promo_discount"] = ext.get("promo_discount", pd.Series(0.0, index=ext.index)).reindex(df.index).fillna(0.0).astype(float)

        df["temperature_max"]  = ext.get("temperature_max", pd.Series(28.0, index=ext.index)).reindex(df.index).fillna(28.0).astype(float)
        df["temperature_min"]  = ext.get("temperature_min", pd.Series(18.0, index=ext.index)).reindex(df.index).fillna(18.0).astype(float)
        df["precipitation_mm"] = ext.get("precipitation_mm", pd.Series(0.0, index=ext.index)).reindex(df.index).fillna(0.0).astype(float)

        holiday_dates = ext[ext["is_holiday"].astype(bool)].index
        df["days_to_next_holiday"] = np.clip(
            df.index.map(
                lambda d: min(
                    ((h - d).days for h in holiday_dates if h >= d),
                    default=30,
                )
            ).to_series().values, 0, 30
        )
    else:
        df["is_holiday"]           = 0
        df["promo_active"]         = 0
        df["promo_discount"]       = 0.0
        df["days_to_next_holiday"] = 30
        df["temperature_max"]      = 28.0
        df["temperature_min"]      = 18.0
        df["precipitation_mm"]     = 0.0

    # ── Features de Interacción ──────────────────────────────────────────────
    df["weekend_x_mean7"]  = df["is_weekend"] * df["rolling_mean_7"].fillna(0)
    df["payday_x_mean7"]   = df["is_payday"]  * df["rolling_mean_7"].fillna(0)
    df["holiday_x_std7"]   = df["is_holiday"]  * df["rolling_std_7"].fillna(0)

    # ── Atributo del Producto ────────────────────────────────────────────────
    df["shelf_life_days"] = shelf_life_days

    # ── Eliminar filas con NaN por ventanas de lag ───────────────────────────
    # lag_28 es el más largo (excl. lag_365 que usa fillna), necesitamos al menos 28+1 días
    before = len(df)
    df = df.dropna(subset=["lag_28", "rolling_mean_21"])
    logger.debug(f"[FeatureEng] Filas tras dropna: {len(df)}/{before}")

    return df.reset_index()
