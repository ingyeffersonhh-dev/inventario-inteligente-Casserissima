"""
CASSERISISSIMA 2.0 — Seed de Datos con 3 Escenarios de Demostración

ESCENARIO 1 — "CORTO" (Dic 2025 → May 2026, ~172 días)
  Historia mínima real. El motor trabaja pero con mayor incertidumbre.
  Demuestra el sistema funcionando con datos limitados.

ESCENARIO 2 — "ÓPTIMO" (May 2024 → May 2026, ~730 días)
  Historia completa de 2 años. El lag_365 es real, los patrones estacionales
  son capturados con precisión. Demuestra el sistema en su mejor estado.

ESCENARIO 3 — "CRÍTICO" (Oct 2025 → May 2026, ~230 días con anomalías)
  Alta variabilidad en ventas, stockouts simulados, picos inesperados
  de demanda y inventario crítico. Demuestra las alarmas y la resiliencia del sistema.

Volumen base: 3-6 tortas diarias en total (pastelería artesanal venezolana).
"""
import json
import logging
import random
from datetime import date, timedelta, datetime, timezone

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from db.models import Product, SaleTransaction, Ingredient, ScenarioConfig, ModelRegistry

logger = logging.getLogger(__name__)

# Seeds distintos por escenario para reproducibilidad
SCENARIO_SEEDS = {1: 42, 2: 123, 3: 777}

# ─── CATÁLOGO DE PRODUCTOS ────────────────────────────────────────────────────

PRODUCTS = [
    # Tortas frías
    {"id": "TF-001", "sku": "TF-3LECHES", "name": "3leches",               "category": "Tortas frías", "selling_price": 20.0, "unit_cost": 10.0, "shelf_life_days": 4, "lead_time_days": 1, "weight": 0.12},
    {"id": "TF-002", "sku": "TF-HELADO",  "name": "Helado Sureño",         "category": "Tortas frías", "selling_price": 22.0, "unit_cost": 11.0, "shelf_life_days": 4, "lead_time_days": 1, "weight": 0.10},
    {"id": "TF-003", "sku": "TF-BESO",    "name": "Beso de amor",          "category": "Tortas frías", "selling_price": 25.0, "unit_cost": 12.0, "shelf_life_days": 4, "lead_time_days": 1, "weight": 0.08},
    {"id": "TF-004", "sku": "TF-PARCH",   "name": "Parchita",              "category": "Tortas frías", "selling_price": 18.0, "unit_cost": 9.0,  "shelf_life_days": 4, "lead_time_days": 1, "weight": 0.08},
    {"id": "TF-005", "sku": "TF-DULCE",   "name": "Dulcemaria",            "category": "Tortas frías", "selling_price": 23.0, "unit_cost": 11.5, "shelf_life_days": 4, "lead_time_days": 1, "weight": 0.07},
    {"id": "TF-006", "sku": "TF-MARQ",    "name": "Marquesa de chocolate", "category": "Tortas frías", "selling_price": 21.0, "unit_cost": 10.5, "shelf_life_days": 4, "lead_time_days": 1, "weight": 0.10},
    
    # Tortas Caseras
    {"id": "TC-001", "sku": "TC-CHOCB",   "name": "Chocolate brownie",     "category": "Tortas Caseras", "selling_price": 18.0, "unit_cost": 9.0,  "shelf_life_days": 5, "lead_time_days": 1, "weight": 0.10},
    {"id": "TC-002", "sku": "TC-PINA",    "name": "Piña",                  "category": "Tortas Caseras", "selling_price": 19.0, "unit_cost": 9.5,  "shelf_life_days": 4, "lead_time_days": 1, "weight": 0.08},
    {"id": "TC-003", "sku": "TC-MARM",    "name": "Marmoleada",            "category": "Tortas Caseras", "selling_price": 15.0, "unit_cost": 7.5,  "shelf_life_days": 5, "lead_time_days": 1, "weight": 0.08},
    {"id": "TC-004", "sku": "TC-VAIN",    "name": "Vainilla",              "category": "Tortas Caseras", "selling_price": 14.0, "unit_cost": 7.0,  "shelf_life_days": 5, "lead_time_days": 1, "weight": 0.07},
    {"id": "TC-005", "sku": "TC-OVO",     "name": "Ovomaltina",            "category": "Tortas Caseras", "selling_price": 22.0, "unit_cost": 11.0, "shelf_life_days": 4, "lead_time_days": 1, "weight": 0.07},
    {"id": "TC-006", "sku": "TC-ZANH",    "name": "Zanahoria",             "category": "Tortas Caseras", "selling_price": 18.0, "unit_cost": 9.0,  "shelf_life_days": 5, "lead_time_days": 1, "weight": 0.05},
]

# ─── FERIADOS VENEZOLANOS 2024-2026 ──────────────────────────────────────────

VENEZUELA_HOLIDAYS: set[date] = {
    # 2024
    date(2024, 1, 1),  date(2024, 2, 12), date(2024, 2, 13),
    date(2024, 3, 28), date(2024, 3, 29), date(2024, 4, 19),
    date(2024, 5, 1),  date(2024, 6, 24), date(2024, 7, 5),
    date(2024, 7, 24), date(2024, 10, 12),
    date(2024, 12, 17),date(2024, 12, 24),date(2024, 12, 25),date(2024, 12, 31),
    # 2025
    date(2025, 1, 1),  date(2025, 3, 3),  date(2025, 3, 4),
    date(2025, 4, 17), date(2025, 4, 18), date(2025, 4, 19),
    date(2025, 5, 1),  date(2025, 6, 24), date(2025, 7, 5),
    date(2025, 7, 24), date(2025, 10, 12),
    date(2025, 12, 17),date(2025, 12, 24),date(2025, 12, 25),date(2025, 12, 31),
    # 2026
    date(2026, 1, 1),  date(2026, 2, 16), date(2026, 2, 17),
    date(2026, 4, 2),  date(2026, 4, 3),  date(2026, 4, 19),
    date(2026, 5, 1),  date(2026, 5, 22),
}

SCENARIO_META = {
    1: {
        "id": 1,
        "name": "Corto",
        "label": "📅 Corto (Dic 2025 – May 2026)",
        "description": "~172 días de historia real. El motor opera con datos mínimos: MAPE más alto, intervalos de confianza más amplios. Representa el estado inicial de un negocio que acaba de adoptar el sistema.",
        "color": "#E8A04A",
        "days": 172,
        "start": date(2025, 12, 1),
    },
    2: {
        "id": 2,
        "name": "Óptimo",
        "label": "🏆 Óptimo (May 2024 – May 2026)",
        "description": "~730 días de historia completa (2 años). El lag_365 captura patrones estacionales reales. MAPE mínimo, intervalos estrechos. Demuestra el sistema en su punto de máxima precisión.",
        "color": "#2ECC71",
        "days": 730,
        "start": date(2024, 5, 23),
    },
    3: {
        "id": 3,
        "name": "Crítico",
        "label": "⚠️ Crítico (Estrés + Anomalías)",
        "description": "Historia de 8 meses con alta variabilidad, picos de demanda inesperados, días de stockout y 3 insumos en nivel crítico. Demuestra las alarmas, la resiliencia del motor y la detección de anomalías.",
        "color": "#E74C3C",
        "days": 243,
        "start": date(2025, 9, 22),
    },
}


def _is_payday(d: date) -> bool:
    return d.day in {14, 15, 28, 29, 30, 31}


def _day_multiplier_base(d: date) -> float:
    """Multiplicador de demanda base (común a los 3 escenarios)."""
    mult = 1.0
    if d.weekday() >= 5:         # Fin de semana
        mult *= 1.35
    if _is_payday(d):             # Quincena venezolana
        mult *= 1.25
    if d in VENEZUELA_HOLIDAYS:   # Feriado festivo
        mult *= 1.40
    if d.weekday() == 0:          # Lunes lento
        mult *= 0.80
    # Diciembre = mes pico de pastelerías
    if d.month == 12:
        mult *= 1.50
    # Febrero = Carnaval (aumento moderado)
    if d.month == 2:
        mult *= 1.20
    return mult


# ─── GENERADOR ESCENARIO 1: CORTO (Dic 2025 – May 2026) ─────────────────────

def _generate_scenario_1() -> list[dict]:
    """
    Historia corta: ~172 días.
    Datos realistas pero el modelo tendrá mayor MAPE por historia limitada.
    No hay lag_365 real → el sistema usa EWM(span=60) como aproximación.
    """
    np.random.seed(SCENARIO_SEEDS[1])
    meta = SCENARIO_META[1]
    end_date = date.today() - timedelta(days=1)
    start_date = meta["start"]
    raw_w = [p["weight"] for p in PRODUCTS]
    weights = np.array(raw_w, dtype=float)
    weights = weights / weights.sum()   # normalizar para evitar error de punto flotante
    records = []
    current = start_date

    while current <= end_date:
        mult = _day_multiplier_base(current)
        daily_total = max(3, min(6, int(round(np.random.poisson(4.0 * mult)))))
        counts = np.random.multinomial(daily_total, weights)

        for prod, count in zip(PRODUCTS, counts):
            qty = float(min(2, count))
            records.append({
                "scenario_id":   1,
                "product_id":    prod["id"],
                "sale_date":     current,
                "quantity_sold": qty,
                "revenue":       round(qty * prod["selling_price"], 2),
                "day_of_week":   current.weekday(),
                "is_holiday":    current in VENEZUELA_HOLIDAYS,
                "is_payday":     _is_payday(current),
            })
        current += timedelta(days=1)

    logger.info(f"[Seed] Escenario 1 (Corto): {len(records)} registros, "
                f"{(end_date - start_date).days + 1} días")
    return records


# ─── GENERADOR ESCENARIO 2: ÓPTIMO (May 2024 – May 2026) ────────────────────

def _generate_scenario_2() -> list[dict]:
    """
    Historia larga: ~730 días (2 años completos).
    El lag_365 captura los patrones de diciembre, carnaval y Semana Santa.
    La primera mitad (2024) tiene un crecimiento gradual de ventas para
    simular un negocio que fue creciendo con el tiempo.
    """
    np.random.seed(SCENARIO_SEEDS[2])
    meta = SCENARIO_META[2]
    end_date = date.today() - timedelta(days=1)
    start_date = meta["start"]
    raw_w2 = [p["weight"] for p in PRODUCTS]
    weights = np.array(raw_w2, dtype=float)
    weights = weights / weights.sum()
    records = []
    current = start_date
    total_days = (end_date - start_date).days + 1

    day_num = 0
    while current <= end_date:
        # Curva de crecimiento gradual: el negocio empezó más lento y fue creciendo
        # Factor de madurez: va de 0.75 (inicio) a 1.0 (presente) en 730 días
        maturity = 0.75 + 0.25 * min(1.0, day_num / 365.0)

        mult = _day_multiplier_base(current) * maturity
        daily_total = max(3, min(6, int(round(np.random.poisson(4.2 * mult)))))
        counts = np.random.multinomial(daily_total, weights)

        for prod, count in zip(PRODUCTS, counts):
            qty = float(min(2, count))
            records.append({
                "scenario_id":   2,
                "product_id":    prod["id"],
                "sale_date":     current,
                "quantity_sold": qty,
                "revenue":       round(qty * prod["selling_price"], 2),
                "day_of_week":   current.weekday(),
                "is_holiday":    current in VENEZUELA_HOLIDAYS,
                "is_payday":     _is_payday(current),
            })
        current += timedelta(days=1)
        day_num += 1

    logger.info(f"[Seed] Escenario 2 (Óptimo): {len(records)} registros, {total_days} días")
    return records


# ─── GENERADOR ESCENARIO 3: CRÍTICO (Estrés + Anomalías) ────────────────────

def _generate_scenario_3() -> list[dict]:
    """
    Escenario de estrés para demostrar las capacidades del sistema ante:
    - Alta variabilidad (CV ~40%): ventas muy irregulares
    - Picos inesperados: 2-3 eventos donde se venden 8-10 tortas en un día
    - Rachas frías: semanas con casi 0 ventas (simulando crisis económica)
    - Stockout implícito: días donde la cantidad es 0 aunque el multiplicador es alto
    - Tendencia positiva reciente (las últimas 6 semanas mejoran)
    """
    np.random.seed(SCENARIO_SEEDS[3])
    meta = SCENARIO_META[3]
    end_date = date.today() - timedelta(days=1)
    start_date = meta["start"]
    raw_w3 = [p["weight"] for p in PRODUCTS]
    weights = np.array(raw_w3, dtype=float)
    weights = weights / weights.sum()
    records = []
    current = start_date
    total_days = (end_date - start_date).days + 1
    day_num = 0

    # Definir periodos de crisis (rachas frías)
    crisis_periods = [
        (date(2025, 10, 5), date(2025, 10, 18)),   # Crisis 1: 2 semanas bajas
        (date(2025, 12, 8), date(2025, 12, 14)),    # Crisis 2: semana pre-quincena
        (date(2026, 2, 1),  date(2026, 2, 8)),      # Crisis 3: post-carnaval
    ]

    # Definir picos anómalos (eventos especiales no predecibles)
    spike_days = {
        date(2025, 11, 15),  # Graduación de colegio cercano
        date(2025, 12, 20),  # Fiesta empresarial
        date(2026, 1, 10),   # Evento de comunidad
        date(2026, 3, 21),   # Boda inesperada
    }

    def _in_crisis(d: date) -> bool:
        return any(s <= d <= e for s, e in crisis_periods)

    while current <= end_date:
        # Tendencia de recuperación en los últimos 42 días
        days_to_end = (end_date - current).days
        recovery_boost = 1.0 if days_to_end > 42 else (1.0 + 0.4 * (1 - days_to_end / 42))

        mult = _day_multiplier_base(current) * recovery_boost

        if current in spike_days:
            # Pico anómalo: 8-10 tortas en un día (2x-2.5x el máximo normal)
            daily_total = int(np.random.uniform(8, 11))
        elif _in_crisis(current):
            # Crisis: solo 0-2 tortas en el día
            daily_total = int(np.random.choice([0, 1, 1, 2, 2], p=[0.2, 0.3, 0.3, 0.1, 0.1]))
        else:
            # Alta variabilidad: ruido extra con distribución negativa-binomial
            base = np.random.poisson(3.8 * mult)
            noise = np.random.choice([-1, 0, 0, 1, 2], p=[0.15, 0.35, 0.25, 0.15, 0.10])
            daily_total = max(0, min(7, base + noise))

        if daily_total == 0:
            # Día sin ventas: insertar ceros para todos los productos
            for prod in PRODUCTS:
                records.append({
                    "scenario_id":   3,
                    "product_id":    prod["id"],
                    "sale_date":     current,
                    "quantity_sold": 0.0,
                    "revenue":       0.0,
                    "day_of_week":   current.weekday(),
                    "is_holiday":    current in VENEZUELA_HOLIDAYS,
                    "is_payday":     _is_payday(current),
                })
        else:
            counts = np.random.multinomial(daily_total, weights)
            for prod, count in zip(PRODUCTS, counts):
                # En picos, permitir hasta 4 unidades de un producto
                max_qty = 4 if current in spike_days else 2
                qty = float(min(max_qty, count))
                records.append({
                    "scenario_id":   3,
                    "product_id":    prod["id"],
                    "sale_date":     current,
                    "quantity_sold": qty,
                    "revenue":       round(qty * prod["selling_price"], 2),
                    "day_of_week":   current.weekday(),
                    "is_holiday":    current in VENEZUELA_HOLIDAYS,
                    "is_payday":     _is_payday(current),
                })

        current += timedelta(days=1)
        day_num += 1

    logger.info(f"[Seed] Escenario 3 (Crítico): {len(records)} registros, {total_days} días")
    return records


# ─── INVENTARIO POR ESCENARIO ─────────────────────────────────────────────────

INGREDIENTS_BY_SCENARIO = {
    1: [  # Corto: niveles normales con algunos amarillos
        {"name": "Harina de Trigo",       "unit": "kg",   "current_stock": 8.5,  "alert_threshold": 3.0},
        {"name": "Azúcar",                "unit": "kg",   "current_stock": 6.0,  "alert_threshold": 2.5},
        {"name": "Huevos",                "unit": "unid", "current_stock": 48.0, "alert_threshold": 12.0},
        {"name": "Leche Condensada",      "unit": "latas","current_stock": 9.0,  "alert_threshold": 3.0},
        {"name": "Leche Evaporada",       "unit": "latas","current_stock": 7.0,  "alert_threshold": 3.0},
        {"name": "Arequipe",              "unit": "kg",   "current_stock": 2.5,  "alert_threshold": 1.0},
        {"name": "Chocolate (Cobertura)", "unit": "kg",   "current_stock": 3.0,  "alert_threshold": 1.0},
        {"name": "Fresas",                "unit": "kg",   "current_stock": 1.5,  "alert_threshold": 0.5},
    ],
    2: [  # Óptimo: stock bien abastecido
        {"name": "Harina de Trigo",       "unit": "kg",   "current_stock": 15.0, "alert_threshold": 3.0},
        {"name": "Azúcar",                "unit": "kg",   "current_stock": 12.0, "alert_threshold": 2.5},
        {"name": "Huevos",                "unit": "unid", "current_stock": 84.0, "alert_threshold": 12.0},
        {"name": "Leche Condensada",      "unit": "latas","current_stock": 18.0, "alert_threshold": 3.0},
        {"name": "Leche Evaporada",       "unit": "latas","current_stock": 14.0, "alert_threshold": 3.0},
        {"name": "Arequipe",              "unit": "kg",   "current_stock": 5.5,  "alert_threshold": 1.0},
        {"name": "Chocolate (Cobertura)", "unit": "kg",   "current_stock": 6.0,  "alert_threshold": 1.0},
        {"name": "Fresas",                "unit": "kg",   "current_stock": 4.0,  "alert_threshold": 0.5},
    ],
    3: [  # Crítico: 3 insumos en nivel rojo, 2 en amarillo
        {"name": "Harina de Trigo",       "unit": "kg",   "current_stock": 2.1,  "alert_threshold": 3.0},   # 🔴 CRÍTICO
        {"name": "Azúcar",                "unit": "kg",   "current_stock": 1.8,  "alert_threshold": 2.5},   # 🔴 CRÍTICO
        {"name": "Huevos",                "unit": "unid", "current_stock": 9.0,  "alert_threshold": 12.0},  # 🔴 CRÍTICO
        {"name": "Leche Condensada",      "unit": "latas","current_stock": 3.5,  "alert_threshold": 3.0},   # 🟡 BAJO
        {"name": "Leche Evaporada",       "unit": "latas","current_stock": 4.0,  "alert_threshold": 3.0},   # ✅ OK
        {"name": "Arequipe",              "unit": "kg",   "current_stock": 0.8,  "alert_threshold": 1.0},   # 🔴 CRÍTICO
        {"name": "Chocolate (Cobertura)", "unit": "kg",   "current_stock": 1.2,  "alert_threshold": 1.0},   # 🟡 BAJO
        {"name": "Fresas",                "unit": "kg",   "current_stock": 1.0,  "alert_threshold": 0.5},   # ✅ OK
    ],
}


# ─── FUNCIÓN PRINCIPAL DE SEED ────────────────────────────────────────────────

def run_seed(db: Session) -> dict:
    """
    Ejecuta el seed completo: productos, 3 escenarios de ventas e inventario.
    Idempotente: verifica si los datos ya existen antes de insertar.
    Activa el Escenario 1 por defecto.
    """
    stats = {"products": 0, "sales_s1": 0, "sales_s2": 0, "sales_s3": 0, "ingredients": 0}

    # ── 1. Productos ─────────────────────────────────────────────────────────
    existing_ids = {p.id for p in db.query(Product).all()}
    for p_data in PRODUCTS:
        if p_data["id"] not in existing_ids:
            prod = Product(
                id=p_data["id"], sku=p_data["sku"], name=p_data["name"],
                category=p_data["category"], selling_price=p_data["selling_price"],
                unit_cost=p_data["unit_cost"], shelf_life_days=p_data["shelf_life_days"],
                lead_time_days=p_data["lead_time_days"], min_order_qty=1, is_active=True,
            )
            db.add(prod)
            stats["products"] += 1
    db.commit()
    logger.info(f"[Seed] Productos: {stats['products']} nuevos / {len(PRODUCTS)} total")

    # ── 2. Tres escenarios de ventas ─────────────────────────────────────────
    generators = {
        1: (_generate_scenario_1, "sales_s1"),
        2: (_generate_scenario_2, "sales_s2"),
        3: (_generate_scenario_3, "sales_s3"),
    }

    for scenario_id, (gen_fn, stat_key) in generators.items():
        existing = db.query(SaleTransaction).filter(
            SaleTransaction.scenario_id == scenario_id
        ).count()
        if existing == 0:
            records = gen_fn()
            batch_size = 500
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                db.execute(SaleTransaction.__table__.insert(), batch)
                db.commit()
            stats[stat_key] = len(records)
            logger.info(f"[Seed] Escenario {scenario_id}: {len(records)} registros insertados")
        else:
            logger.info(f"[Seed] Escenario {scenario_id}: ya tiene {existing} registros. Skipping.")

    # ── 3. Inventario (solo si no existe) ────────────────────────────────────
    from db.models import Ingredient
    existing_ing = db.query(Ingredient).count()
    if existing_ing == 0:
        # Insertar los 3 sets de ingredientes con un campo scenario_id implícito
        # Usamos el del escenario 1 como estado actual del sistema
        for ing_data in INGREDIENTS_BY_SCENARIO[1]:
            ing = Ingredient(**ing_data)
            db.add(ing)
        db.commit()
        stats["ingredients"] = len(INGREDIENTS_BY_SCENARIO[1])

    # ── 4. Configuración de escenario activo (singleton) ────────────────────
    from db.models import ScenarioConfig
    config = db.query(ScenarioConfig).first()
    if not config:
        db.add(ScenarioConfig(id=1, active_scenario=1))
        db.commit()
        logger.info("[Seed] ScenarioConfig inicializado → Escenario 1 (Corto) activo")

    return {**stats, "scenario_meta": SCENARIO_META}


def get_active_scenario(db: Session) -> int:
    """Retorna el ID del escenario activo (1, 2 o 3)."""
    config = db.query(ScenarioConfig).first()
    return config.active_scenario if config else 1


def set_active_scenario(scenario_id: int, db: Session) -> dict:
    """Cambia el escenario activo y actualiza los niveles de inventario."""
    if scenario_id not in (1, 2, 3):
        raise ValueError(f"Escenario inválido: {scenario_id}. Debe ser 1, 2 o 3.")

    config = db.query(ScenarioConfig).first()
    if not config:
        config = ScenarioConfig(id=1, active_scenario=scenario_id)
        db.add(config)
    else:
        config.active_scenario = scenario_id

    # Actualizar inventario al del escenario seleccionado
    from db.models import Ingredient
    ingredients = db.query(Ingredient).all()
    scenario_ing = {i["name"]: i for i in INGREDIENTS_BY_SCENARIO[scenario_id]}
    for ing in ingredients:
        if ing.name in scenario_ing:
            ing.current_stock = scenario_ing[ing.name]["current_stock"]

    db.commit()
    logger.info(f"[Scenario] Cambiado a escenario {scenario_id}: {SCENARIO_META[scenario_id]['name']}")
    return SCENARIO_META[scenario_id]
