"""
CASSERISISSIMA 2.0 — Router: Backtesting / Validación Walk-Forward (OE4)
GET /api/v1/backtest/summary — lee results/backtest_resumen.json y lo retorna verbatim.
"""
import logging
import os
import json

from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter()

# Repo root resolved relative to this file (src/routers -> src -> repo root).
# Mirrors the convention in core/ml/backtest_report.py (REPO_ROOT / RESULTS_DIR).
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_RESULTS_FILE = os.path.join(_REPO_ROOT, "results", "backtest_resumen.json")


@router.get("/backtest/summary")
def get_backtest_summary():
    """
    Retorna el resumen del backtest walk-forward (escenario activo) tal cual
    fue generado por scripts/regenerar_backtest.py. El archivo vive en
    results/backtest_resumen.json y no se regenera aquí.
    """
    if not os.path.exists(_RESULTS_FILE):
        raise HTTPException(
            status_code=404,
            detail="Backtest results not found. Run `python scripts/regenerar_backtest.py` first.",
        )
    try:
        with open(_RESULTS_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Error leyendo %s: %s", _RESULTS_FILE, exc)
        raise HTTPException(
            status_code=500,
            detail="Backtest results file is unreadable. Re-run `python scripts/regenerar_backtest.py`.",
        ) from exc
    return data