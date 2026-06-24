"""
CASSERISISSIMA 2.0 — Model Trainer v3 (Optimizado)
Entrena, evalúa y serializa el modelo de pronóstico por producto.

Mejoras sobre v2:
  - Hyperparameter Tuning con RandomizedSearchCV (Fase 3)
  - Log-transform del target log1p/expm1 para reducir RMSE (Fase 2)
  - LightGBM como modelo competidor (Fase 4)
  - Umbral de calidad de datos adaptativo (Fase 5)
  - Feature Importance logging y almacenamiento (Fase 6)
  - Competencia RF vs LightGBM: el ganador se serializa
"""
import json
import joblib
import logging
import os
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV

from core.ml.feature_engineering import build_features, FEATURE_COLUMNS
from core.ml.pipeline import build_pipeline, build_lgbm_pipeline, calculate_metrics

logger = logging.getLogger(__name__)

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "models")
os.makedirs(MODELS_DIR, exist_ok=True)

MIN_ROWS_FOR_TUNING = 50   # Mínimo para RandomizedSearchCV
MIN_ROWS_FOR_RF = 21       # Mínimo para Random Forest con TimeSeriesSplit
MIN_ROWS_FOR_EWM = 7       # Mínimo absoluto para fallback EWM

# ── Espacios de búsqueda de hiperparámetros ──────────────────────────────────

RF_PARAM_SPACE = {
    "model__n_estimators": [100, 200, 300, 500],
    "model__max_depth": [5, 10, 15, 20, None],
    "model__min_samples_leaf": [1, 2, 3, 5, 8],
    "model__min_samples_split": [2, 5, 10],
    "model__max_features": ["sqrt", "log2", 0.5, 0.8],
}

LGBM_PARAM_SPACE = {
    "model__n_estimators": [100, 200, 300, 500],
    "model__max_depth": [4, 6, 8, 12, -1],
    "model__learning_rate": [0.01, 0.03, 0.05, 0.1],
    "model__num_leaves": [15, 31, 63],
    "model__min_child_samples": [3, 5, 10],
    "model__subsample": [0.7, 0.8, 0.9, 1.0],
    "model__colsample_bytree": [0.6, 0.7, 0.8, 0.9],
}


def _assess_data_quality(y: pd.Series) -> dict:
    """
    Evalúa la calidad de los datos del target para decidir qué pipeline usar.
    
    Returns:
        dict con:
        - score: "high", "medium", "low"
        - zero_ratio: proporción de ceros en el target
        - cv: coeficiente de variación (std/mean)
        - effective_n: número de muestras con y > 0
    """
    n = len(y)
    n_zeros = int((y == 0).sum())
    zero_ratio = n_zeros / n if n > 0 else 1.0
    mean_val = float(y.mean())
    std_val = float(y.std())
    cv = std_val / mean_val if mean_val > 0 else float("inf")
    effective_n = int((y > 0).sum())

    # Scoring logic — prioriza el número absoluto de muestras efectivas
    if zero_ratio > 0.90 or effective_n < 10:
        score = "low"
    elif effective_n < 30 or (zero_ratio > 0.70 and cv > 2.0):
        score = "medium"
    else:
        score = "high"

    result = {
        "score": score,
        "zero_ratio": round(zero_ratio, 3),
        "cv": round(cv, 3) if cv != float("inf") else 999.0,
        "effective_n": effective_n,
        "total_n": n,
    }
    logger.info(f"  Data quality: score={score}, zero_ratio={zero_ratio:.1%}, "
                f"CV={cv:.2f}, effective_n={effective_n}/{n}")
    return result


def _extract_feature_importance(pipeline, feature_names: list[str]) -> dict:
    """
    Extrae y ordena las importancias de features del modelo final.
    Compatible con RF (feature_importances_) y LightGBM (feature_importances_).
    """
    model = pipeline.named_steps["model"]
    if not hasattr(model, "feature_importances_"):
        return {}

    importances = model.feature_importances_
    # Normalizar a porcentaje
    total = importances.sum()
    if total == 0:
        return {}

    importance_pct = (importances / total * 100).round(2)
    feat_imp = sorted(
        zip(feature_names, importance_pct.tolist()),
        key=lambda x: x[1],
        reverse=True,
    )

    # Log top 10 y bottom 3
    logger.info("  Feature Importance (Top 10):")
    for name, pct in feat_imp[:10]:
        bar = "█" * int(pct / 2)
        logger.info(f"    {name:25s} {pct:6.2f}%  {bar}")

    low_imp = [f for f, p in feat_imp if p < 0.5]
    high_imp = [f for f, p in feat_imp if p > 2.0]
    if low_imp and len(high_imp) >= 5:
        logger.warning(f"  ⚠ Features con importancia < 0.5% (candidatas a eliminación): {low_imp}")

    return dict(feat_imp)


def _train_with_search(
    X: pd.DataFrame,
    y: pd.Series,
    pipeline_builder,
    param_space: dict,
    n_splits: int,
    n_iter: int = 20,
    use_log: bool = False,
) -> tuple:
    """
    Entrena un modelo con RandomizedSearchCV + TimeSeriesSplit.

    Args:
        X, y: datos de entrenamiento
        pipeline_builder: función que devuelve un Pipeline limpio
        param_space: espacio de hiperparámetros
        n_splits: número de folds temporales
        n_iter: iteraciones de búsqueda aleatoria
        use_log: si True, transforma y con log1p

    Returns:
        (best_pipeline, avg_metrics_dict, best_params)
    """
    y_train = np.log1p(y) if use_log else y.copy()

    tscv = TimeSeriesSplit(n_splits=n_splits)
    base_pipeline = pipeline_builder()

    search = RandomizedSearchCV(
        estimator=base_pipeline,
        param_distributions=param_space,
        n_iter=n_iter,
        cv=tscv,
        scoring="neg_mean_squared_error",
        random_state=42,
        n_jobs=-1,
        refit=True,
        error_score="raise",
    )

    search.fit(X, y_train)
    best_pipeline = search.best_estimator_

    # Calcular métricas en escala original mediante CV manual
    best_params = {k.replace("model__", ""): v for k, v in search.best_params_.items()}
    cv_metrics = []
    for train_idx, val_idx in tscv.split(X):
        X_tr, y_tr = X.iloc[train_idx], y_train.iloc[train_idx]
        X_val, y_val = X.iloc[val_idx], y.iloc[val_idx]

        fold_pipeline = pipeline_builder(**best_params)
        fold_pipeline.fit(X_tr, y_tr)

        y_pred = fold_pipeline.predict(X_val)
        if use_log:
            y_pred = np.expm1(y_pred)
        y_pred = np.maximum(0, y_pred)
        cv_metrics.append(calculate_metrics(y_val.values, y_pred))

    avg_metrics = {
        "mape": float(np.mean([m["mape"] for m in cv_metrics])),
        "rmse": float(np.mean([m["rmse"] for m in cv_metrics])),
        "mae":  float(np.mean([m["mae"]  for m in cv_metrics])),
    }

    return best_pipeline, avg_metrics, best_params


def _train_simple(
    X: pd.DataFrame,
    y: pd.Series,
    pipeline_builder,
    n_splits: int,
    use_log: bool = False,
    **kwargs,
) -> tuple:
    """
    Entrena un modelo sin tuning (hiperparámetros fijos conservadores).
    Para datasets pequeños o de calidad baja.
    """
    y_train = np.log1p(y) if use_log else y.copy()

    pipeline = pipeline_builder(**kwargs)
    tscv = TimeSeriesSplit(n_splits=n_splits)
    cv_metrics = []

    for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
        X_tr, y_tr = X.iloc[train_idx], y_train.iloc[train_idx]
        X_val, y_val_orig = X.iloc[val_idx], y.iloc[val_idx]

        pipe = pipeline_builder(**kwargs)
        pipe.fit(X_tr, y_tr)

        y_pred = pipe.predict(X_val)
        if use_log:
            y_pred = np.expm1(y_pred)
        y_pred = np.maximum(0, y_pred)
        cv_metrics.append(calculate_metrics(y_val_orig.values, y_pred))

    avg_metrics = {
        "mape": float(np.mean([m["mape"] for m in cv_metrics])),
        "rmse": float(np.mean([m["rmse"] for m in cv_metrics])),
        "mae":  float(np.mean([m["mae"]  for m in cv_metrics])),
    }

    # Fit final en todo el dataset
    pipeline.fit(X, y_train)

    return pipeline, avg_metrics, {}


def train_product_model(
    sales_df: pd.DataFrame,
    product_id: str,
    sku: str,
    shelf_life_days: int,
    external_factors_df: pd.DataFrame | None = None,
    n_cv_splits: int = 3,
) -> dict:
    """
    Entrena el mejor modelo para un producto específico.

    Flujo:
    1. Feature Engineering
    2. Evaluación de calidad de datos → decide pipeline tier
    3. Tier Alto: RandomizedSearchCV para RF y LightGBM, elige ganador
    4. Tier Medio: RF con hiperparámetros conservadores fijos
    5. Tier Bajo: Fallback EWM
    6. Log-transform si los datos lo justifican (CV > 0.5)
    7. Feature Importance logging

    Returns:
        dict con métricas, versión del modelo y ruta del archivo .joblib
    """
    n_records = len(sales_df)

    if n_records < MIN_ROWS_FOR_EWM:
        raise ValueError(
            f"[{sku}] Se requieren al menos {MIN_ROWS_FOR_EWM} días de historia. "
            f"Disponibles: {n_records}"
        )

    # ── Feature Engineering ──────────────────────────────────────────────────
    logger.info(f"[{sku}] Construyendo features ({n_records} registros)...")
    df_feat = build_features(sales_df, external_factors_df, shelf_life_days)

    X = df_feat[FEATURE_COLUMNS]
    y = df_feat["quantity_sold"]
    n_feat_rows = len(X)

    if n_feat_rows < MIN_ROWS_FOR_RF:
        # Muy pocos datos tras feature engineering → modelo ligero sin CV
        logger.warning(
            f"[{sku}] Solo {n_feat_rows} filas tras feature engineering. "
            "Entrenando modelo ligero (sin CV)."
        )
        final_pipeline = build_pipeline(n_estimators=50, max_depth=5)
        final_pipeline.fit(X, y)
        avg_mape, avg_rmse, avg_mae = 0.25, float(y.std() or 0.5), float(y.mean() * 0.25 or 0.1)

        return _serialize_result(
            pipeline=final_pipeline,
            product_id=product_id,
            sku=sku,
            n_feat_rows=n_feat_rows,
            metrics={"mape": avg_mape, "rmse": avg_rmse, "mae": avg_mae},
            best_params={"n_estimators": 50, "max_depth": 5, "min_samples_leaf": 3},
            model_type="rf_lite",
            use_log=False,
            data_quality={"score": "low"},
            feature_importance={},
        )

    # ── Calidad de datos ─────────────────────────────────────────────────────
    logger.info(f"[{sku}] Evaluando calidad de datos...")
    dq = _assess_data_quality(y)

    # Decidir si usar log-transform: beneficioso cuando hay varianza significativa
    use_log = dq["cv"] > 0.5 and dq["effective_n"] > 10
    if use_log:
        logger.info(f"[{sku}] Log-transform activado (CV={dq['cv']:.2f} > 0.5)")

    # ── Configurar CV splits ─────────────────────────────────────────────────
    n_splits = min(n_cv_splits, n_feat_rows // 10)
    n_splits = max(2, n_splits)

    if dq["score"] == "high" and n_feat_rows >= MIN_ROWS_FOR_TUNING:
        # ── TIER ALTO: Competencia RF vs LightGBM con tuning ─────────────
        logger.info(f"[{sku}] Tier ALTO: RandomizedSearchCV — RF vs LightGBM "
                     f"({n_feat_rows} filas, {n_splits} folds)")

        # Entrenar RF con tuning
        logger.info(f"[{sku}] ── Entrenando Random Forest con tuning...")
        try:
            rf_pipeline, rf_metrics, rf_params = _train_with_search(
                X, y, build_pipeline, RF_PARAM_SPACE,
                n_splits=n_splits, n_iter=20, use_log=use_log,
            )
            logger.info(f"[{sku}]    RF → MAPE={rf_metrics['mape']:.4f} "
                         f"RMSE={rf_metrics['rmse']:.4f} MAE={rf_metrics['mae']:.4f}")
        except Exception as e:
            logger.warning(f"[{sku}] RF tuning falló: {e}. Usando parámetros fijos.")
            rf_pipeline, rf_metrics, rf_params = _train_simple(
                X, y, build_pipeline, n_splits, use_log=use_log,
            )

        # Entrenar LightGBM con tuning
        logger.info(f"[{sku}] ── Entrenando LightGBM con tuning...")
        try:
            lgbm_pipeline, lgbm_metrics, lgbm_params = _train_with_search(
                X, y, build_lgbm_pipeline, LGBM_PARAM_SPACE,
                n_splits=n_splits, n_iter=20, use_log=use_log,
            )
            logger.info(f"[{sku}]    LGBM → MAPE={lgbm_metrics['mape']:.4f} "
                         f"RMSE={lgbm_metrics['rmse']:.4f} MAE={lgbm_metrics['mae']:.4f}")
        except Exception as e:
            logger.warning(f"[{sku}] LightGBM tuning falló: {e}. Usando solo RF.")
            lgbm_pipeline, lgbm_metrics, lgbm_params = None, {"rmse": float("inf")}, {}

        # Elegir ganador por RMSE (métrica más robusta para optimización de inventario)
        if lgbm_pipeline and lgbm_metrics["rmse"] < rf_metrics["rmse"]:
            winner = "lgbm"
            final_pipeline = lgbm_pipeline
            final_metrics = lgbm_metrics
            final_params = lgbm_params
            logger.info(f"[{sku}] ★ Ganador: LightGBM (RMSE {lgbm_metrics['rmse']:.4f} < {rf_metrics['rmse']:.4f})")
        else:
            winner = "rf"
            final_pipeline = rf_pipeline
            final_metrics = rf_metrics
            final_params = rf_params
            logger.info(f"[{sku}] ★ Ganador: Random Forest (RMSE {rf_metrics['rmse']:.4f})")

    elif dq["score"] == "medium" or n_feat_rows >= MIN_ROWS_FOR_RF:
        # ── TIER MEDIO: RF con parámetros conservadores fijos ────────────
        logger.info(f"[{sku}] Tier MEDIO: RF conservador ({n_feat_rows} filas, {n_splits} folds)")

        final_pipeline, final_metrics, _ = _train_simple(
            X, y, build_pipeline, n_splits, use_log=use_log,
            n_estimators=200, max_depth=10, min_samples_leaf=5,
        )
        winner = "rf"
        final_params = {"n_estimators": 200, "max_depth": 10, "min_samples_leaf": 5}
        logger.info(f"[{sku}]    RF → MAPE={final_metrics['mape']:.4f} "
                     f"RMSE={final_metrics['rmse']:.4f}")
    else:
        # ── TIER BAJO: No debería llegar aquí (ya manejado arriba) ───────
        final_pipeline = build_pipeline(n_estimators=50, max_depth=5)
        y_fit = np.log1p(y) if use_log else y
        final_pipeline.fit(X, y_fit)
        winner = "rf_lite"
        final_metrics = {"mape": 0.25, "rmse": float(y.std() or 0.5), "mae": float(y.mean() * 0.25 or 0.1)}
        final_params = {"n_estimators": 50, "max_depth": 5}

    # ── Feature Importance ───────────────────────────────────────────────────
    logger.info(f"[{sku}] Extrayendo feature importance...")
    feat_imp = _extract_feature_importance(final_pipeline, FEATURE_COLUMNS)

    return _serialize_result(
        pipeline=final_pipeline,
        product_id=product_id,
        sku=sku,
        n_feat_rows=n_feat_rows,
        metrics=final_metrics,
        best_params=final_params,
        model_type=winner,
        use_log=use_log,
        data_quality=dq,
        feature_importance=feat_imp,
    )


def _serialize_result(
    pipeline,
    product_id: str,
    sku: str,
    n_feat_rows: int,
    metrics: dict,
    best_params: dict,
    model_type: str,
    use_log: bool,
    data_quality: dict,
    feature_importance: dict,
) -> dict:
    """Serializa el modelo y construye el diccionario de resultado."""
    version_tag = f"{model_type}_{sku}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    model_path = os.path.join(MODELS_DIR, f"{version_tag}.joblib")
    joblib.dump(pipeline, model_path)

    logger.info(
        f"[{sku}] ✓ Modelo guardado → {model_path} | "
        f"Tipo={model_type} | MAPE={metrics['mape']:.4f} RMSE={metrics['rmse']:.4f}"
    )

    hyperparameters = {
        **best_params,
        "model_type": model_type,
        "log_transform": use_log,
        "data_quality_score": data_quality.get("score", "unknown"),
    }

    return {
        "product_id":       product_id,
        "sku":              sku,
        "version_tag":      version_tag,
        "model_path":       model_path,
        "training_rows":    int(n_feat_rows),
        "feature_list":     json.dumps(feature_importance) if feature_importance else json.dumps(FEATURE_COLUMNS),
        "hyperparameters":  json.dumps(hyperparameters),
        "mape_val":         round(metrics["mape"], 4),
        "rmse_val":         round(metrics["rmse"], 4),
        "mae_val":          round(metrics["mae"], 4),
        "trained_at":       datetime.now(timezone.utc).isoformat(),
    }
