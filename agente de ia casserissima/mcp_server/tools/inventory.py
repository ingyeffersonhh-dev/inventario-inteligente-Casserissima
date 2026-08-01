from sqlalchemy import select
from typing import Optional
from database.connection import AsyncSessionLocal
from database.models import Ingredient

async def check_inventory(ingredient_id: Optional[int] = None) -> dict:
    """Consulta el stock actual de un insumo específico o de todos si no se provee ID."""
    async with AsyncSessionLocal() as session:
        if ingredient_id:
            result = await session.execute(select(Ingredient).where(Ingredient.id == ingredient_id))
        else:
            result = await session.execute(select(Ingredient))
            
        ingredients = result.scalars().all()
        
        return {
            "ingredients": [
                {
                    "id": i.id,
                    "name": i.name,
                    "stock": i.current_stock,
                    "unit": i.unit,
                    "status": "critical" if i.current_stock <= i.alert_threshold else "ok"
                } for i in ingredients
            ]
        }


async def get_rop_alerts() -> dict:
    """Obtiene alertas de insumos cuyo stock está por debajo del Punto de Reorden (alerta)."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Ingredient).where(Ingredient.current_stock <= Ingredient.alert_threshold)
        )
        ingredients = result.scalars().all()
        
        return {
            "alerts": [
                {
                    "ingredient": i.name,
                    "stock": i.current_stock,
                    "rop_threshold": i.alert_threshold,
                    "deficit": i.alert_threshold - i.current_stock,
                    "action": f"Pedir al menos {i.alert_threshold - i.current_stock + 5} {i.unit}"
                } for i in ingredients
            ]
        }
