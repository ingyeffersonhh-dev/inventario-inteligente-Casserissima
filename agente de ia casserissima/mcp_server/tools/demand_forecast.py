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


async def predict_demand(product_id: str, horizon_days: int = 7) -> dict:
    """
    Consulta el pronóstico de demanda de un producto para los próximos días.
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Product).where(Product.id == product_id)
        )
        prod = result.scalars().first()
        if not prod:
            return {"error": f"Producto {product_id} no encontrado."}

        today = date.today()
        result = await db.execute(
            select(DemandForecast)
            .where(
                DemandForecast.product_id == product_id,
                DemandForecast.forecast_date >= today,
            )
            .order_by(DemandForecast.forecast_date)
            .limit(horizon_days)
        )
        forecasts = result.scalars().all()

        if not forecasts:
            return {"error": "No hay pronósticos recientes. Dile al usuario que debe generar el pronóstico desde el dashboard principal."}

        return {
            "product": prod.name,
            "sku": prod.sku,
            "forecasts": [
                {
                    "date": f.forecast_date.isoformat(),
                    "predicted_qty": max(0, int(round(f.predicted_demand))),
                    "lower_bound": max(0, int(round(f.lower_bound_90))),
                    "upper_bound": max(0, int(round(f.upper_bound_90))),
                }
                for f in forecasts
            ],
        }
