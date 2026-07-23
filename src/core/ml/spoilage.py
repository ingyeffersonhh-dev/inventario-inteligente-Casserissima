"""
CASSERISISSIMA 2.0 — Simulador de Merma (Spoilage) — OE4
Simula el inventario perecedero por producto aplicando vida útil (shelf life).

Regla: una unidad producida el día d que no se vende antes de finalizar el día
d + shelf_life_days se considera merma (spoilage). Se usa FIFO (primero las
unidades más antiguas) para minimizar el desperdicio — política estándar de
manejo de perecederos.

El campo `shelf_life_days` SÍ existe en el modelo `Product` (default=3; seed lo
fija en 4-5 por producto). Aun así se expone un fallback por categoría por si un
producto lo tuviera en NULL o se quisiera sobreescribir en la tesis.
"""
import numpy as np
import pandas as pd
from collections import deque

# ── Fallback de vida útil por categoría (días) ─────────────────────────────────
# Solo se usa si shelf_life_days no viene dado. El modelo Product ya lo tiene,
# pero se documenta como respaldo declarado para la tesis.
SHELF_LIFE_DEFAULTS_BY_CATEGORY: dict[str, int] = {
    "Tortas frías": 4,
    "Tortas Caseras": 5,
    "Postres": 3,
    "Panadería": 3,
}
SHELF_LIFE_FALLBACK = 3  # por defecto global si la categoría no está listada


def resolve_shelf_life(shelf_life_days: int | None, category: str | None = None) -> int:
    """Resuelve la vida útil: dato del producto → fallback por categoría → global."""
    if shelf_life_days and shelf_life_days > 0:
        return int(shelf_life_days)
    if category and category in SHELF_LIFE_DEFAULTS_BY_CATEGORY:
        return SHELF_LIFE_DEFAULTS_BY_CATEGORY[category]
    return SHELF_LIFE_FALLBACK


def simulate_spoilage(
    production: pd.Series | list[float],
    demand: pd.Series | list[float],
    shelf_life_days: int,
    dates: list | None = None,
    round_production: bool = True,
) -> dict:
    """
    Simula inventario perecedero día a día.

    Orden diario (convención documentada):
      1. Envejecer inventario existente.
      2. Recibir la producción del día (edad 0).
      3. Expirar (merma) las unidades con edad >= shelf_life_days.
      4. Atender la demanda con FIFO (unidades más antiguas primero).
      5. El inventario restante pasa al día siguiente.

    Args:
        production: unidades producidas por día (política evaluada).
        demand: demanda real por día (de seed.py).
        shelf_life_days: vida útil.
        dates: fechas (opcional) para el DataFrame resultante.
        round_production: si True, redondea la producción al entero más cercano
            (las tortas son unidades discretas; el modelo emite float).

    Returns:
        dict con:
          - daily: DataFrame[date, produced, demanded, sold, wasted, eod_stock, cumulative_waste]
          - waste_pct:  wasted / produced (sobre todo el periodo)
          - fill_rate:  sold / demanded (nivel de servicio / fill rate)
          - total_produced, total_demanded, total_sold, total_wasted
    """
    prod_arr = np.asarray(production, dtype=float)
    dem_arr = np.asarray(demand, dtype=float)
    if len(prod_arr) != len(dem_arr):
        raise ValueError(
            f"production y demand deben tener igual longitud ({len(prod_arr)} != {len(dem_arr)})."
        )
    if round_production:
        prod_arr = np.rint(np.maximum(prod_arr, 0.0))
    dem_arr = np.maximum(dem_arr, 0.0)

    shelf = max(1, int(shelf_life_days))

    # Cola FIFO de lotes: cada lote = (cantidad_restante, edad_en_días)
    queue: deque = deque()
    total_produced = 0.0
    total_demanded = 0.0
    total_sold = 0.0
    total_wasted = 0.0
    cumulative_waste = 0.0

    rows = []
    n = len(prod_arr)

    for i in range(n):
        # 1. Envejecer
        queue = deque((qty, age + 1) for qty, age in queue)

        # 2. Recibir producción del día
        p = float(prod_arr[i])
        if p > 0:
            queue.append((p, 0))
        total_produced += p

        # 3. Expirar lotes con edad >= shelf
        wasted_today = 0.0
        remaining: deque = deque()
        for qty, age in queue:
            if age >= shelf:
                wasted_today += qty
            else:
                remaining.append((qty, age))
        queue = remaining
        total_wasted += wasted_today
        cumulative_waste += wasted_today

        # 4. Atender demanda FIFO (más antiguos primero)
        d = float(dem_arr[i])
        total_demanded += d
        sold_today = 0.0
        to_serve = d
        new_queue: deque = deque()
        for qty, age in queue:
            if to_serve <= 0:
                new_queue.append((qty, age))
                continue
            take = min(qty, to_serve)
            sold_today += take
            to_serve -= take
            leftover = qty - take
            if leftover > 0:
                new_queue.append((leftover, age))
        queue = new_queue
        total_sold += sold_today

        # 5. EOD stock
        eod_stock = sum(q for q, _ in queue)

        rows.append({
            "idx": i,
            "produced": p,
            "demanded": d,
            "sold": sold_today,
            "wasted": wasted_today,
            "eod_stock": eod_stock,
            "cumulative_waste": cumulative_waste,
        })

    waste_pct = (total_wasted / total_produced) if total_produced > 0 else 0.0
    fill_rate = (total_sold / total_demanded) if total_demanded > 0 else 0.0

    daily = pd.DataFrame(rows)
    if dates is not None and len(dates) == n:
        daily.insert(0, "date", dates)

    return {
        "daily": daily,
        "waste_pct": float(waste_pct),
        "fill_rate": float(fill_rate),
        "total_produced": float(total_produced),
        "total_demanded": float(total_demanded),
        "total_sold": float(total_sold),
        "total_wasted": float(total_wasted),
    }