"""
CASSERISISSIMA 2.0 — Pipeline ML v3 (Optimizado)
Encapsula preprocesamiento + modelo en pipelines scikit-learn serializables.

Mejoras sobre v2:
  - Eliminado StandardScaler (innecesario para RF y LightGBM)
  - Soporte para log-transform del target en predict_with_intervals
  - Pipeline LightGBM como alternativa competidora
"""
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
from core.ml.feature_engineering import FEATURE_COLUMNS


def build_pipeline(
    n_estimators: int = 200,
    max_depth: int = 15,
    min_samples_leaf: int = 3,
    min_samples_split: int = 2,
    max_features: str | float = "sqrt",
    random_state: int = 42,
) -> Pipeline:
    """
    Construye el pipeline scikit-learn para Random Forest:
    SimpleImputer → RandomForestRegressor

    StandardScaler eliminado: RF es invariante a la escala de features.
    """
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_leaf=min_samples_leaf,
            min_samples_split=min_samples_split,
            max_features=max_features,
            random_state=random_state,
            n_jobs=4,
            oob_score=True,
        )),
    ])


def build_lgbm_pipeline(
    n_estimators: int = 300,
    max_depth: int = 8,
    learning_rate: float = 0.05,
    num_leaves: int = 31,
    min_child_samples: int = 5,
    subsample: float = 0.8,
    colsample_bytree: float = 0.8,
    reg_alpha: float = 0.1,
    reg_lambda: float = 0.1,
    random_state: int = 42,
) -> Pipeline:
    """
    Construye el pipeline scikit-learn para LightGBM:
    SimpleImputer → LGBMRegressor

    Hiperparámetros optimizados para series temporales de baja volumetría
    (pastelería artesanal, 3-6 unidades diarias).
    """
    from lightgbm import LGBMRegressor

    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", LGBMRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            num_leaves=num_leaves,
            min_child_samples=min_child_samples,
            subsample=subsample,
            colsample_bytree=colsample_bytree,
            reg_alpha=reg_alpha,
            reg_lambda=reg_lambda,
            random_state=random_state,
            verbose=-1,
            n_jobs=4,
        )),
    ])


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """
    Calcula métricas de error para ajustar el stock de seguridad dinámico.
    Maneja días sin venta (evita división por cero en MAPE).
    """
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)

    mask = y_true > 0
    mape = mean_absolute_percentage_error(y_true[mask], y_pred[mask]) if mask.sum() > 0 else 0.0
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae  = float(np.mean(np.abs(y_true - y_pred)))

    return {
        "mape": round(float(mape), 4),
        "rmse": round(rmse, 4),
        "mae":  round(mae, 4),
    }


def predict_with_intervals(
    pipeline: Pipeline,
    X: pd.DataFrame,
    confidence: float = 0.90,
    registry: dict | None = None,
) -> pd.DataFrame:
    """
    Genera pronósticos puntuales + intervalos de confianza.

    Para Random Forest: usa la varianza entre árboles (distribución empírica).
    Para LightGBM: usa una aproximación basada en desviación estándar del error.

    Si el modelo fue entrenado con log-transform, aplica expm1 a las predicciones.

    Args:
        pipeline:   Pipeline entrenado (con named_steps["model"])
        X:          Features para predecir
        confidence: Nivel de confianza (0.90 = 90%)
        registry:   Dict con metadatos del modelo (para detectar log-transform)

    Returns:
        DataFrame con columnas ['predicted', 'lower', 'upper']
    """
    # Detectar si el modelo usó log-transform
    use_log = False
    if registry:
        hp_raw = registry.get("hyperparameters", "{}")
        if isinstance(hp_raw, str):
            try:
                hp = json.loads(hp_raw)
            except Exception:
                hp = {}
        else:
            hp = hp_raw
        use_log = hp.get("log_transform", False)

    model = pipeline.named_steps["model"]
    X_transformed = pipeline[:-1].transform(X[FEATURE_COLUMNS])

    # Detectar tipo de modelo
    is_rf = hasattr(model, "estimators_")

    if is_rf:
        # Random Forest: distribución empírica de árboles
        tree_predictions = np.array([
            tree.predict(X_transformed) for tree in model.estimators_
        ])  # shape: (n_estimators, n_samples)

        alpha = (1 - confidence) / 2
        lower = np.quantile(tree_predictions, alpha, axis=0)
        upper = np.quantile(tree_predictions, 1 - alpha, axis=0)
        point = np.mean(tree_predictions, axis=0)

        if use_log:
            point = np.expm1(point)
            lower = np.expm1(lower)
            upper = np.expm1(upper)
    else:
        # LightGBM: aproximación por desviación estándar
        from scipy import stats
        point = model.predict(X_transformed)
        # Estimar sigma como porcentaje del valor predicho (heurística)
        sigma = np.maximum(np.abs(point) * 0.15, 0.1)
        z = stats.norm.ppf(1 - (1 - confidence) / 2)
        lower = point - z * sigma
        upper = point + z * sigma

        if use_log:
            point = np.expm1(point)
            lower = np.expm1(lower)
            upper = np.expm1(upper)

    return pd.DataFrame({
        "predicted": np.maximum(0, point).round(2),
        "lower":     np.maximum(0, lower).round(2),
        "upper":     np.maximum(0, upper).round(2),
    })
