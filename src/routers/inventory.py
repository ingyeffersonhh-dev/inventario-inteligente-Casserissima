"""
CASSERISISSIMA 2.0 — Router: Inventario de Insumos
GET  /api/v1/inventory          — estado actual de todos los insumos
PUT  /api/v1/inventory/{id}     — actualizar stock de un insumo
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import Ingredient

router = APIRouter()
logger = logging.getLogger(__name__)


class IngredientUpdateRequest(BaseModel):
    current_stock: float = Field(ge=0.0)


@router.get("/inventory")
def get_inventory(db: Session = Depends(get_db)):
    """Lista todos los insumos con su estado actual y clasificación RAG."""
    ingredients = db.query(Ingredient).order_by(Ingredient.name).all()
    items = []
    for ing in ingredients:
        ratio = ing.current_stock / ing.alert_threshold if ing.alert_threshold > 0 else 2.0
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
    return {"ingredients": items, "total": len(items)}


@router.put("/inventory/{ingredient_id}")
def update_ingredient_stock(
    ingredient_id: int,
    req: IngredientUpdateRequest,
    db: Session = Depends(get_db),
):
    """Actualiza el stock actual de un insumo."""
    ing = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not ing:
        raise HTTPException(status_code=404, detail=f"Insumo {ingredient_id} no encontrado.")
    ing.current_stock = req.current_stock
    db.commit()
    logger.info(f"[Inventory] {ing.name}: stock actualizado a {req.current_stock} {ing.unit}")
    return {
        "status":        "ok",
        "ingredient":    ing.name,
        "new_stock":     round(ing.current_stock, 2),
        "unit":          ing.unit,
        "alert_threshold": ing.alert_threshold,
    }
