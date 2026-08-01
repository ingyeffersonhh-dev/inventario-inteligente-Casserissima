import sys
import os

from config.settings import settings
from database.connection import AsyncSessionLocal

# Import models from the main system's src/ package
_src_path = os.path.join(settings.main_system_path, "src")
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)

from db.models import Product, DemandForecast
from datetime import date
from sqlalchemy import select
from core.operations_research.newsvendor import calculate_critical_ratio, newsvendor_optimal_quantity


async def calculate_optimal_production(product_id: str) -> dict:
    """
    Calcula la cantidad óptima a producir usando el Modelo Newsvendor
    basado en la predicción de demanda de hoy.
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Product).where(Product.id == product_id)
        )
        prod = result.scalars().first()
        if not prod:
            return {"error": f"Producto {product_id} no encontrado."}

        today = date.today()

        # Tomamos el pronóstico de los próximos 7 días para promediar la demanda reciente
        result = await db.execute(
            select(DemandForecast)
            .where(
                DemandForecast.product_id == product_id,
                DemandForecast.forecast_date >= today,
            )
            .order_by(DemandForecast.forecast_date)
            .limit(7)
        )
        forecasts = result.scalars().all()

        if not forecasts:
            return {"error": "No hay pronóstico reciente para calcular Newsvendor."}

        # Promedio de la demanda de los próximos 7 días (o los días disponibles)
        avg_demand = sum(f.predicted_demand for f in forecasts) / len(forecasts)
        rmse = forecasts[0].rmse if forecasts[0].rmse else 0.5

        cr = calculate_critical_ratio(prod.unit_cost, prod.selling_price)

        newsvendor = newsvendor_optimal_quantity(
            mu_demand=avg_demand * prod.lead_time_days,
            sigma_demand=rmse * (prod.lead_time_days ** 0.5),
            critical_ratio=cr,
        )

        # Backend newsvendor_optimal_quantity returns {"q_star", "q_star_rounded", "service_level_at_q"}
        return {
            "product": prod.name,
            "optimal_qty_to_produce": max(0, int(round(newsvendor["q_star_rounded"]))),
            "critical_ratio": round(cr, 4),
            "avg_daily_demand": round(avg_demand, 2),
            "service_level_at_q": round(float(newsvendor.get("service_level_at_q", 0.0)), 4),
            "q_star": float(newsvendor["q_star"]),
        }
