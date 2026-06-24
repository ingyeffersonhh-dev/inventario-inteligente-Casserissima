"""
CASSERISISSIMA 2.0 — Router: Gestión de Escenarios de Demostración
GET  /api/v1/scenarios           — lista los 3 escenarios disponibles
GET  /api/v1/scenarios/active    — escenario activo actual
PUT  /api/v1/scenarios/{id}      — cambia el escenario activo
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from db.seed import SCENARIO_META, get_active_scenario, set_active_scenario

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/scenarios")
def list_scenarios(db: Session = Depends(get_db)):
    """Retorna la descripción de los 3 escenarios de demostración."""
    active = get_active_scenario(db)
    scenarios = []
    for sid, meta in SCENARIO_META.items():
        scenarios.append({
            "id":          meta["id"],
            "name":        meta["name"],
            "label":       meta["label"],
            "description": meta["description"],
            "color":       meta["color"],
            "days":        meta["days"],
            "is_active":   (sid == active),
        })
    return {"scenarios": scenarios, "active_scenario_id": active}


@router.get("/scenarios/active")
def get_active(db: Session = Depends(get_db)):
    """Retorna el escenario activo con sus metadatos."""
    active_id = get_active_scenario(db)
    meta = SCENARIO_META[active_id]
    return {
        "id":          meta["id"],
        "name":        meta["name"],
        "label":       meta["label"],
        "description": meta["description"],
        "color":       meta["color"],
        "days":        meta["days"],
    }


@router.put("/scenarios/{scenario_id}")
def switch_scenario(scenario_id: int, db: Session = Depends(get_db)):
    """
    Cambia el escenario de demostración activo.
    Actualiza el inventario al estado correspondiente al escenario.
    """
    if scenario_id not in (1, 2, 3):
        raise HTTPException(status_code=400, detail="Escenario inválido. Use 1, 2 o 3.")
    try:
        meta = set_active_scenario(scenario_id, db)
        logger.info(f"Escenario cambiado a: {scenario_id} ({meta['name']})")
        return {
            "status":   "ok",
            "message":  f"Escenario '{meta['name']}' activado correctamente.",
            "scenario": meta,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
