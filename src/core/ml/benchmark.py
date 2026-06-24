"""
CASSERISISSIMA 2.0 — Benchmark ML v3
Script para comparar métricas del modelo optimizado vs. baseline.

Uso:
    cd backend
    python -m core.ml.benchmark
"""
import sys
import os
import logging
import time

# Agregar backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd
from datetime import date, timedelta

from db.database import SessionLocal, init_db
from db.models import Product, SaleTransaction
from db.seed import get_active_scenario, set_active_scenario, SCENARIO_META
from core.ml.model_trainer import train_product_model
from core.ml.feature_engineering import FEATURE_COLUMNS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("benchmark")


def run_benchmark(scenario_id: int = 2, max_products: int | None = None):
    """
    Ejecuta el benchmark entrenando todos los productos del escenario dado.
    
    Args:
        scenario_id: Escenario a usar (2 = Óptimo recomendado)
        max_products: Limitar a N productos (None = todos)
    """
    init_db()
    db = SessionLocal()

    try:
        # Asegurar escenario correcto
        set_active_scenario(scenario_id, db)
        meta = SCENARIO_META[scenario_id]
        logger.info(f"\n{'='*70}")
        logger.info(f"  BENCHMARK ML v3 — Escenario {scenario_id}: {meta['name']}")
        logger.info(f"  {meta['description'][:80]}...")
        logger.info(f"{'='*70}\n")

        # Obtener productos activos
        products = db.query(Product).filter(Product.is_active == True).all()
        if max_products:
            products = products[:max_products]

        results = []
        total_start = time.time()

        for idx, prod in enumerate(products, 1):
            logger.info(f"\n{'─'*60}")
            logger.info(f"  [{idx}/{len(products)}] {prod.name} ({prod.sku})")
            logger.info(f"{'─'*60}")

            # Cargar historial
            sales_rows = (
                db.query(SaleTransaction.sale_date, SaleTransaction.quantity_sold)
                .filter(
                    SaleTransaction.scenario_id == scenario_id,
                    SaleTransaction.product_id == prod.id,
                )
                .order_by(SaleTransaction.sale_date)
                .all()
            )

            if len(sales_rows) < 7:
                logger.warning(f"  ⚠ Solo {len(sales_rows)} registros. Saltando.")
                continue

            sales_df = pd.DataFrame(
                [(r.sale_date.isoformat(), float(r.quantity_sold)) for r in sales_rows],
                columns=["sale_date", "quantity_sold"]
            )

            start = time.time()
            try:
                result = train_product_model(
                    sales_df=sales_df,
                    product_id=prod.id,
                    sku=prod.sku,
                    shelf_life_days=prod.shelf_life_days,
                    n_cv_splits=3,
                )
                elapsed = time.time() - start

                results.append({
                    "sku":          prod.sku,
                    "name":         prod.name,
                    "model_type":   result.get("version_tag", "").split("_")[0],
                    "mape":         result["mape_val"],
                    "rmse":         result["rmse_val"],
                    "mae":          result["mae_val"],
                    "rows":         result["training_rows"],
                    "time_s":       round(elapsed, 1),
                })

                logger.info(f"  ✓ {result['version_tag']}")
                logger.info(f"    MAPE={result['mape_val']:.4f}  RMSE={result['rmse_val']:.4f}  "
                           f"MAE={result['mae_val']:.4f}  ({elapsed:.1f}s)")

            except Exception as e:
                logger.error(f"  ✗ Error: {e}")
                results.append({
                    "sku":        prod.sku,
                    "name":       prod.name,
                    "model_type": "ERROR",
                    "mape":       None,
                    "rmse":       None,
                    "mae":        None,
                    "rows":       len(sales_rows),
                    "time_s":     round(time.time() - start, 1),
                })

        total_elapsed = time.time() - total_start

        # ── Resumen ──────────────────────────────────────────────────────────
        logger.info(f"\n{'='*70}")
        logger.info(f"  RESUMEN DEL BENCHMARK")
        logger.info(f"{'='*70}")

        df = pd.DataFrame(results)
        if not df.empty and df["mape"].notna().any():
            valid = df[df["mape"].notna()]
            logger.info(f"\n  Productos entrenados: {len(valid)}/{len(products)}")
            logger.info(f"  Tiempo total: {total_elapsed:.1f}s")
            logger.info(f"\n  {'SKU':<15} {'Tipo':<8} {'MAPE':>8} {'RMSE':>8} {'MAE':>8} {'Filas':>6} {'t(s)':>6}")
            logger.info(f"  {'─'*15} {'─'*8} {'─'*8} {'─'*8} {'─'*8} {'─'*6} {'─'*6}")
            for _, r in valid.iterrows():
                logger.info(
                    f"  {r['sku']:<15} {r['model_type']:<8} "
                    f"{r['mape']:>8.4f} {r['rmse']:>8.4f} {r['mae']:>8.4f} "
                    f"{r['rows']:>6} {r['time_s']:>6.1f}"
                )

            logger.info(f"\n  {'PROMEDIOS':<15} {'':8} "
                         f"{valid['mape'].mean():>8.4f} {valid['rmse'].mean():>8.4f} "
                         f"{valid['mae'].mean():>8.4f}")

            # Distribución de modelos ganadores
            if "model_type" in valid.columns:
                type_counts = valid["model_type"].value_counts()
                logger.info(f"\n  Modelos ganadores:")
                for mt, count in type_counts.items():
                    logger.info(f"    {mt}: {count} productos")

        logger.info(f"\n{'='*70}\n")

        return df

    finally:
        db.close()


if __name__ == "__main__":
    # Por defecto: Escenario 2 (Óptimo), todos los productos
    scenario = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    max_prod = int(sys.argv[2]) if len(sys.argv) > 2 else None
    run_benchmark(scenario_id=scenario, max_products=max_prod)
