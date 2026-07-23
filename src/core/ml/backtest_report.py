"""
CASSERISISSIMA 2.0 — Reporte de Backtesting + Merma + Comparativa (OE4)
Unifica walk-forward backtest (backtest.py), simulador de merma (spoilage.py)
y comparador baseline (baseline.py) en un solo reporte serializable.

Salida:
    - JSON a stdout (con --json)
    - CSV por producto y agregado a results/ (con --csv)
    - Resumen legible a stdout (default)

Uso (desde src/):
    python -m core.ml.backtest_report --scenario 2 --max-products 3
    python -m core.ml.backtest_report --scenario 2 --json --csv

Smoke (1 producto, ventana corta):
    python -m core.ml.backtest_report --smoke
"""
import sys
import os
import json
import argparse
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from db.database import SessionLocal, init_db
from db.models import Product, SaleTransaction
from db.seed import set_active_scenario, SCENARIO_META
from core.ml.backtest import walk_forward_backtest, DEFAULT_TRAIN_WINDOW_DAYS, DEFAULT_HORIZON_DAYS, DEFAULT_RETRAIN_EVERY_DAYS
from core.ml.baseline import compare_policies, DEFAULT_BASELINE_K, DEFAULT_BASELINE_BUFFER
from core.ml.spoilage import resolve_shelf_life

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("backtest_report")

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RESULTS_DIR = os.path.join(REPO_ROOT, "results")


# ── Smoke config: 1 producto, ventana corta, horizonte corto ──────────────────
SMOKE_TRAIN_WINDOW = 45    # ≥35 para que build_features deje ≥7 filas-feature (lag_28)
SMOKE_HORIZON = 7
SMOKE_RETRAIN_EVERY = 7
SMOKE_MAX_WINDOWS = 5


def _load_product_sales(db, scenario_id: int, product: Product) -> pd.DataFrame:
    rows = (
        db.query(SaleTransaction.sale_date, SaleTransaction.quantity_sold)
        .filter(
            SaleTransaction.scenario_id == scenario_id,
            SaleTransaction.product_id == product.id,
        )
        .order_by(SaleTransaction.sale_date)
        .all()
    )
    if not rows:
        return pd.DataFrame(columns=["sale_date", "quantity_sold"])
    return pd.DataFrame(
        [(r.sale_date.isoformat(), float(r.quantity_sold)) for r in rows],
        columns=["sale_date", "quantity_sold"],
    )


def _daily_demand_series(sales_df: pd.DataFrame) -> pd.Series:
    df = sales_df.copy()
    df["sale_date"] = pd.to_datetime(df["sale_date"])
    df = df.sort_values("sale_date").drop_duplicates(subset="sale_date").set_index("sale_date")
    full = pd.date_range(df.index.min(), df.index.max(), freq="D")
    s = df["quantity_sold"].reindex(full).fillna(0.0).astype(float)
    s.index.name = "sale_date"
    return s


def run_full_report(
    scenario_id: int = 2,
    max_products: int | None = None,
    train_window_days: int = DEFAULT_TRAIN_WINDOW_DAYS,
    horizon: int = DEFAULT_HORIZON_DAYS,
    retrain_every: int = DEFAULT_RETRAIN_EVERY_DAYS,
    baseline_k: int = DEFAULT_BASELINE_K,
    baseline_buffer: float = DEFAULT_BASELINE_BUFFER,
    products_only: list[str] | None = None,
    max_windows: int | None = None,
) -> dict:
    """
    Ejecuta backtest + merma + comparativa para (un subconjunto de) productos.

    Returns:
        dict serializable con:
          - config
          - per_product: {product_id: {sku, name, aggregated_metrics, comparison, ...}}
          - aggregated: medias sobre productos válidos
          - summary: string legible
    """
    init_db()
    db = SessionLocal()
    try:
        set_active_scenario(scenario_id, db)
        meta = SCENARIO_META[scenario_id]
        logger.info("=" * 70)
        logger.info(f"  OE4 BACKTEST — Escenario {scenario_id}: {meta['name']}")
        logger.info("=" * 70)

        q = db.query(Product).filter(Product.is_active == True)
        if products_only:
            q = q.filter(Product.id.in_(products_only))
        products = q.all()
        if max_products:
            products = products[:max_products]

        per_product: dict = {}
        agg_records: list[dict] = []

        for idx, prod in enumerate(products, 1):
            logger.info(f"\n[{idx}/{len(products)}] {prod.name} ({prod.sku}) — shelf_life={prod.shelf_life_days}d")
            sales_df = _load_product_sales(db, scenario_id, prod)
            if len(sales_df) < max(train_window_days + horizon, 30):
                logger.warning(f"  Historia insuficiente ({len(sales_df)}). Saltando.")
                continue

            shelf = resolve_shelf_life(prod.shelf_life_days, prod.category)

            # 1) Walk-forward backtest
            try:
                bt = walk_forward_backtest(
                    sales_df=sales_df,
                    product_id=prod.id,
                    sku=prod.sku,
                    shelf_life_days=shelf,
                    train_window_days=train_window_days,
                    horizon=horizon,
                    retrain_every=retrain_every,
                    max_windows=max_windows,
                )
            except ValueError as e:
                logger.warning(f"  Backtest saltado: {e}")
                continue

            agg = bt["aggregated"]
            logger.info(f"  Backtest: {agg['n_windows']} ventanas, {agg['n_predictions']} pred — "
                        f"MAE={agg.get('mae')} MAPE={agg.get('mape')} RMSE={agg.get('rmse')}")

            # 2+3) Comparativa baseline vs sistema (merma + fill rate)
            preds_df = pd.DataFrame(bt["predictions"])
            demand_series = _daily_demand_series(sales_df)
            cmp = compare_policies(
                predictions_df=preds_df,
                demand_series=demand_series,
                shelf_life_days=shelf,
                baseline_k=baseline_k,
                baseline_buffer=baseline_buffer,
            )

            c = cmp["comparison"]
            logger.info(f"  Merma: sistema={c['waste_pct_system']*100:.2f}% vs "
                        f"baseline={c['waste_pct_baseline']*100:.2f}% "
                        f"(reducción {c['waste_reduction_pct']:.2f}%)")
            logger.info(f"  Fill rate: sistema={c['fill_rate_system']*100:.2f}% vs "
                        f"baseline={c['fill_rate_baseline']*100:.2f}% "
                        f"(Δ {c['fill_rate_delta']*100:+.2f}%)")

            per_product[prod.id] = {
                "sku": prod.sku,
                "name": prod.name,
                "category": prod.category,
                "shelf_life_days": shelf,
                "aggregated_metrics": agg,
                "comparison": c,
                "baseline_params": cmp["baseline_params"],
                "n_days_compared": cmp["n_days"],
                "n_windows": agg["n_windows"],
                "n_predictions": agg["n_predictions"],
            }
            agg_records.append({
                "product_id": prod.id,
                "sku": prod.sku,
                "name": prod.name,
                "category": prod.category,
                "shelf_life_days": shelf,
                "mae": agg.get("mae"),
                "mape": agg.get("mape"),
                "rmse": agg.get("rmse"),
                "waste_pct_system": c["waste_pct_system"],
                "waste_pct_baseline": c["waste_pct_baseline"],
                "waste_reduction_pct": c["waste_reduction_pct"],
                "fill_rate_system": c["fill_rate_system"],
                "fill_rate_baseline": c["fill_rate_baseline"],
                "fill_rate_delta": c["fill_rate_delta"],
                "n_windows": agg["n_windows"],
                "n_predictions": agg["n_predictions"],
            })

        # ── Agregados sobre productos válidos ──
        if agg_records:
            agg_df = pd.DataFrame(agg_records)
            numeric_cols = [c for c in agg_df.columns if c not in
                            ("product_id", "sku", "name", "category")]
            aggregated = {
                "n_products": int(len(agg_df)),
                "mean_mae": float(agg_df["mae"].dropna().mean()),
                "mean_mape": float(agg_df["mape"].dropna().mean()),
                "mean_rmse": float(agg_df["rmse"].dropna().mean()),
                "mean_waste_pct_system": float(agg_df["waste_pct_system"].mean()),
                "mean_waste_pct_baseline": float(agg_df["waste_pct_baseline"].mean()),
                "mean_waste_reduction_pct": float(agg_df["waste_reduction_pct"].mean()),
                "mean_fill_rate_system": float(agg_df["fill_rate_system"].mean()),
                "mean_fill_rate_baseline": float(agg_df["fill_rate_baseline"].mean()),
                "mean_fill_rate_delta": float(agg_df["fill_rate_delta"].mean()),
            }
        else:
            aggregated = {"n_products": 0}

        summary = (
            f"OE4 Backtest (escenario {scenario_id}, {aggregated.get('n_products',0)} productos): "
            f"MAE medio={aggregated.get('mean_mae')}, MAPE medio={aggregated.get('mean_mape')}, "
            f"merma sistema={aggregated.get('mean_waste_pct_system',0)*100:.2f}% vs "
            f"baseline={aggregated.get('mean_waste_pct_baseline',0)*100:.2f}% "
            f"(reducción media {aggregated.get('mean_waste_reduction_pct',0):.2f}%), "
            f"fill rate sistema={aggregated.get('mean_fill_rate_system',0)*100:.2f}% vs "
            f"baseline={aggregated.get('mean_fill_rate_baseline',0)*100:.2f}%."
        )

        return {
            "config": {
                "scenario_id": scenario_id,
                "scenario_name": meta["name"],
                "train_window_days": train_window_days,
                "horizon": horizon,
                "retrain_every": retrain_every,
                "baseline_k": baseline_k,
                "baseline_buffer": baseline_buffer,
                "max_products": max_products,
            },
            "per_product": per_product,
            "aggregated": aggregated,
            "aggregated_table": agg_records,
            "summary": summary,
        }
    finally:
        db.close()


def write_csv_outputs(report: dict, out_dir: str = RESULTS_DIR) -> list[str]:
    """Escribe CSVs (tabla agregada + tabla por producto + per-window si está disponible)."""
    os.makedirs(out_dir, exist_ok=True)
    paths = []

    agg_df = pd.DataFrame(report.get("aggregated_table", []))
    if not agg_df.empty:
        p = os.path.join(out_dir, "backtest_agregado.csv")
        agg_df.to_csv(p, index=False, encoding="utf-8-sig")
        paths.append(p)

    # Per-product flat table
    rows = []
    for pid, info in report.get("per_product", {}).items():
        rows.append({
            "product_id": pid,
            "sku": info["sku"],
            "name": info["name"],
            "category": info["category"],
            "shelf_life_days": info["shelf_life_days"],
            "n_windows": info["n_windows"],
            "n_predictions": info["n_predictions"],
            "mae": info["aggregated_metrics"].get("mae"),
            "mape": info["aggregated_metrics"].get("mape"),
            "rmse": info["aggregated_metrics"].get("rmse"),
            **info["comparison"],
        })
    if rows:
        pp_df = pd.DataFrame(rows)
        p = os.path.join(out_dir, "backtest_por_producto.csv")
        pp_df.to_csv(p, index=False, encoding="utf-8-sig")
        paths.append(p)

    # Full report (config + per_product + aggregated + aggregated_table + summary)
    p = os.path.join(out_dir, "backtest_resumen.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(_json_safe(report), f, ensure_ascii=False, indent=2)
    paths.append(p)

    return paths


def _json_safe(obj):
    """Convierte tipos numpy/pandas a tipos nativos para JSON."""
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if pd.isna(obj) if not isinstance(obj, (dict, list, tuple)) else False:
        return None
    return obj


def main():
    parser = argparse.ArgumentParser(description="OE4 — Walk-forward backtest + merma + comparativa")
    parser.add_argument("--scenario", type=int, default=2, help="Escenario (1=Corto, 2=Óptimo, 3=Crítico)")
    parser.add_argument("--max-products", type=int, default=None, help="Limitar a N productos")
    parser.add_argument("--products", type=str, default=None, help="Lista de product_id separados por coma")
    parser.add_argument("--train-window", type=int, default=DEFAULT_TRAIN_WINDOW_DAYS)
    parser.add_argument("--horizon", type=int, default=DEFAULT_HORIZON_DAYS)
    parser.add_argument("--retrain-every", type=int, default=DEFAULT_RETRAIN_EVERY_DAYS)
    parser.add_argument("--baseline-k", type=int, default=DEFAULT_BASELINE_K)
    parser.add_argument("--baseline-buffer", type=float, default=DEFAULT_BASELINE_BUFFER)
    parser.add_argument("--smoke", action="store_true", help="Smoke: 1 producto, ventana=30, horizonte=7")
    parser.add_argument("--json", action="store_true", help="Imprimir reporte completo en JSON")
    parser.add_argument("--csv", action="store_true", help="Escribir CSVs a results/")
    args = parser.parse_args()

    products_only = None
    if args.products:
        products_only = [p.strip() for p in args.products.split(",") if p.strip()]

    if args.smoke:
        # Smoke: tomar 1 producto (el primero activo) con ventana corta
        init_db()
        db = SessionLocal()
        try:
            set_active_scenario(args.scenario, db)
            first = db.query(Product).filter(Product.is_active == True).first()
            products_only = [first.id] if first else None
        finally:
            db.close()
        train_window = SMOKE_TRAIN_WINDOW
        horizon = SMOKE_HORIZON
        retrain_every = SMOKE_RETRAIN_EVERY
        max_windows = SMOKE_MAX_WINDOWS
        logger.info("SMOKE MODE: 1 producto, train_window=45, horizon=7, max_windows=5")
    else:
        train_window = args.train_window
        horizon = args.horizon
        retrain_every = args.retrain_every
        max_windows = None

    report = run_full_report(
        scenario_id=args.scenario,
        max_products=args.max_products,
        train_window_days=train_window,
        horizon=horizon,
        retrain_every=retrain_every,
        baseline_k=args.baseline_k,
        baseline_buffer=args.baseline_buffer,
        products_only=products_only,
        max_windows=max_windows,
    )

    print("\n" + "=" * 70)
    print("  RESUMEN OE4")
    print("=" * 70)
    print(f"\n{report['summary']}\n")

    if args.csv:
        paths = write_csv_outputs(report)
        for p in paths:
            print(f"  CSV/JSON escrito: {p}")

    if args.json:
        print("\n" + "-" * 70)
        print(json.dumps(_json_safe(report), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
