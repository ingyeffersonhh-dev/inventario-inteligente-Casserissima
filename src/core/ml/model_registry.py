"""
CASSERISISSIMA 2.0 — Model Registry (Reescrito para SQLite)
Gestión de versiones de modelos ML: carga, activación y lookup.
"""
import json
import joblib
import logging
import os
from typing import Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sklearn.pipeline import Pipeline

from db.models import ModelRegistry
from core.ml.feature_engineering import FEATURE_COLUMNS

logger = logging.getLogger(__name__)


def register_model(train_result: dict, db: Session) -> int:
    """
    Registra un modelo entrenado en la tabla model_registry y lo activa,
    desactivando la versión anterior del mismo producto.

    Returns: ID del registro creado
    """
    product_id = train_result["product_id"]

    # Desactivar modelo anterior
    db.query(ModelRegistry).filter(
        ModelRegistry.product_id == product_id,
        ModelRegistry.is_active == True,
    ).update({"is_active": False})

    record = ModelRegistry(
        product_id=product_id,
        version_tag=train_result["version_tag"],
        training_rows=train_result["training_rows"],
        feature_list=train_result.get("feature_list"),
        hyperparameters=train_result.get("hyperparameters"),
        mape_val=train_result["mape_val"],
        rmse_val=train_result["rmse_val"],
        mae_val=train_result.get("mae_val", 0.0),
        storage_path=train_result["model_path"],
        is_active=True,
        trained_at=datetime.now(timezone.utc),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    logger.info(f"Modelo registrado: {train_result['version_tag']} → ID {record.id}")
    return record.id


def load_active_model(product_id: str, db: Session) -> Optional[tuple[Pipeline, dict]]:
    """
    Carga el modelo activo de un producto desde disco local.
    Valida que las features coincidan con las esperadas por el código actual.

    Returns:
        (pipeline, registry_dict) o None si no hay modelo activo o hay incompatibilidad
    """
    record = (
        db.query(ModelRegistry)
        .filter(
            ModelRegistry.product_id == product_id,
            ModelRegistry.is_active == True,
        )
        .order_by(ModelRegistry.trained_at.desc())
        .first()
    )

    if not record:
        logger.warning(f"No hay modelo activo para producto {product_id}")
        return None

    # Validar compatibilidad de features para evitar errores de scikit-learn
    if record.feature_list:
        try:
            feats = json.loads(record.feature_list)
            if isinstance(feats, dict):
                model_features = list(feats.keys())
            elif isinstance(feats, list):
                model_features = feats
            else:
                model_features = []

            # Verificar si las features coinciden exactamente
            if set(model_features) != set(FEATURE_COLUMNS):
                logger.warning(
                    f"El modelo {record.version_tag} tiene features incompatibles. "
                    f"Esperadas: {len(FEATURE_COLUMNS)}, Encontradas en modelo: {len(model_features)}. "
                    f"Desactivando modelo para forzar reentrenamiento."
                )
                record.is_active = False
                db.commit()
                return None
        except Exception as e:
            logger.error(f"Error al validar lista de features: {e}. Desactivando modelo por seguridad.")
            record.is_active = False
            db.commit()
            return None
    else:
        # Si no tiene lista de features guardada, forzar reentrenamiento por seguridad
        logger.warning(f"Modelo {record.version_tag} no tiene metadatos de features. Desactivando para reentrenar.")
        record.is_active = False
        db.commit()
        return None

    if not record.storage_path or not os.path.exists(record.storage_path):
        logger.error(f"Archivo de modelo no encontrado: {record.storage_path}")
        return None

    pipeline = joblib.load(record.storage_path)
    logger.info(f"Modelo cargado: {record.version_tag}")

    return pipeline, {
        "version_tag": record.version_tag,
        "mape_val":    record.mape_val,
        "rmse_val":    record.rmse_val,
        "mae_val":     record.mae_val,
        "training_rows": record.training_rows,
        "trained_at":  record.trained_at.isoformat() if record.trained_at else None,
    }
