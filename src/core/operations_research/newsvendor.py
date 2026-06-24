"""
CASSERIISSIMA 2.0 — Modelo Newsvendor (Conservado de v1)
Calcula la cantidad óptima de pedido bajo incertidumbre asimétrica de costos.
Referencia: Porteus (2002) "Foundations of Stochastic Inventory Theory"
"""
import numpy as np
from scipy import stats


def calculate_critical_ratio(
    unit_cost: float,
    selling_price: float,
    salvage_value: float = 0.0,
    stockout_penalty: float = 0.0,
) -> float:
    cu = selling_price - unit_cost + stockout_penalty
    co = unit_cost - salvage_value
    if (cu + co) <= 0:
        raise ValueError("Cu + Co debe ser positivo.")
    cr = cu / (cu + co)
    return float(np.clip(cr, 0.01, 0.99))


def newsvendor_optimal_quantity(
    mu_demand: float,
    sigma_demand: float,
    critical_ratio: float,
    min_order: int = 1,
) -> dict:
    if sigma_demand <= 0:
        sigma_demand = mu_demand * 0.15
    q_star = float(stats.norm.ppf(critical_ratio, loc=mu_demand, scale=sigma_demand))
    q_star = max(float(min_order), q_star)
    service_level_at_q = float(stats.norm.cdf(q_star, loc=mu_demand, scale=sigma_demand))
    return {
        "q_star":              round(q_star, 2),
        "q_star_rounded":      int(np.ceil(q_star)),
        "service_level_at_q":  round(service_level_at_q, 4),
        "critical_ratio":      round(critical_ratio, 4),
        "mu_demand":           round(mu_demand, 2),
        "sigma_demand":        round(sigma_demand, 2),
    }
