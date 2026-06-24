"""
CASSERISISSIMA 2.0 — Smoke Test Post-Migration
Verifies that the backend/ → src/ rename didn't break any imports.

Usage:
    cd src
    python -m pytest ../tests/test_smoke.py -v
"""
import sys
import os

# Add src/ to path (same as main.py does)
SRC_DIR = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, SRC_DIR)


def test_imports_feature_engineering():
    """Feature engineering module loads correctly."""
    from core.ml.feature_engineering import build_features, FEATURE_COLUMNS
    assert len(FEATURE_COLUMNS) > 30, f"Expected 30+ features, got {len(FEATURE_COLUMNS)}"


def test_imports_pipeline():
    """ML pipeline module loads correctly."""
    from core.ml.pipeline import build_pipeline, build_lgbm_pipeline, calculate_metrics
    pipeline = build_pipeline()
    assert pipeline is not None


def test_imports_model_trainer():
    """Model trainer module loads correctly."""
    from core.ml.model_trainer import train_product_model
    assert callable(train_product_model)


def test_imports_operations_research():
    """Operations research modules load correctly."""
    from core.operations_research.newsvendor import (
        calculate_critical_ratio,
        newsvendor_optimal_quantity,
    )
    from core.operations_research.reorder_point import calculate_reorder_point

    # Quick sanity check
    cr = calculate_critical_ratio(unit_cost=5.0, selling_price=15.0)
    assert 0 < cr < 1, f"Critical ratio should be between 0 and 1, got {cr}"


def test_imports_database():
    """Database module loads correctly."""
    from db.database import init_db, SessionLocal
    assert callable(init_db)


def test_imports_models():
    """ORM models load correctly."""
    from db.models import Product, SaleTransaction, DemandForecast, ModelRegistry
    assert hasattr(Product, "sku")
    assert hasattr(SaleTransaction, "quantity_sold")


def test_imports_routers():
    """Router modules load correctly."""
    from routers import dashboard, sales, predictions, insights, scenarios
    assert hasattr(dashboard, "router")
    assert hasattr(sales, "router")


def test_fastapi_app():
    """FastAPI application initializes correctly."""
    from main import app
    assert app.title == "CASSERISSIMA 2.0 — Motor Predictivo"
    assert app.version == "2.0.0"


def test_newsvendor_calculation():
    """Newsvendor model produces valid output."""
    from core.operations_research.newsvendor import (
        calculate_critical_ratio,
        newsvendor_optimal_quantity,
    )

    cr = calculate_critical_ratio(unit_cost=5.0, selling_price=15.0)
    result = newsvendor_optimal_quantity(
        mu_demand=3.0, sigma_demand=1.0, critical_ratio=cr
    )
    assert result["q_star"] > 0
    assert result["q_star_rounded"] >= 1
    assert 0 < result["service_level_at_q"] <= 1


if __name__ == "__main__":
    tests = [
        test_imports_feature_engineering,
        test_imports_pipeline,
        test_imports_model_trainer,
        test_imports_operations_research,
        test_imports_database,
        test_imports_models,
        test_imports_routers,
        test_fastapi_app,
        test_newsvendor_calculation,
    ]

    print("=" * 60)
    print("  SMOKE TEST — Post-Migration Verification")
    print("=" * 60)

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            print(f"  [OK] {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {test.__name__}: {e}")
            failed += 1

    print(f"\n  Results: {passed} passed, {failed} failed")
    print("=" * 60)

    sys.exit(1 if failed > 0 else 0)
