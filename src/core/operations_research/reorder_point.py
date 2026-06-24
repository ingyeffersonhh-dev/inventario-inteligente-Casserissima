"""
CASSERIISSIMA 2.0 — Punto de Reorden Evolutivo (Conservado de v1)
ROP recalculado en cada ciclo, penalizando por MAPE y RMSE históricos.
Referencia: Silver, Pyke & Peterson (1998)
"""
import numpy as np
from scipy import stats


def calculate_reorder_point(
    avg_daily_demand: float,
    demand_std_daily: float,
    lead_time_days: int,
    mape: float,
    rmse: float,
    service_level: float = 0.97,
    demand_variability_during_lt: bool = True,
) -> dict:
    z_score = float(stats.norm.ppf(service_level))
    mu_lead_time = avg_daily_demand * lead_time_days

    if demand_variability_during_lt:
        sigma_base = demand_std_daily * np.sqrt(lead_time_days)
    else:
        sigma_base = demand_std_daily * lead_time_days

    mape_penalty  = 1.0 + float(np.clip(mape, 0, 1.0))
    rmse_buffer   = float(np.sqrt(lead_time_days)) * rmse * 0.5
    sigma_adjusted = sigma_base * mape_penalty
    safety_stock  = z_score * sigma_adjusted + rmse_buffer
    rop = mu_lead_time + safety_stock

    return {
        "rop":                 round(float(rop), 2),
        "safety_stock":        round(float(safety_stock), 2),
        "mu_lead_time":        round(float(mu_lead_time), 2),
        "sigma_base":          round(float(sigma_base), 2),
        "sigma_adjusted":      round(float(sigma_adjusted), 2),
        "mape_penalty_factor": round(float(mape_penalty), 4),
        "rmse_buffer":         round(float(rmse_buffer), 2),
        "z_score":             round(float(z_score), 4),
        "service_level":       service_level,
        "lead_time_days":      lead_time_days,
    }


def evaluate_reorder_urgency(current_stock: float, rop: float, avg_daily_demand: float) -> str:
    if avg_daily_demand <= 0:
        return "sin_alerta"
    days_of_stock = current_stock / avg_daily_demand
    if current_stock <= 0:
        return "crítico"
    elif current_stock <= rop * 0.5:
        return "crítico"
    elif current_stock <= rop:
        return "crítico" if days_of_stock < 2 else "alto"
    elif current_stock <= rop * 1.2:
        return "normal"
    else:
        return "sin_alerta"
