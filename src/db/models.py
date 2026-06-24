"""
CASSERISSIMA 2.0 — ORM Models (SQLAlchemy)
Modelos de base de datos para el sistema de pastelería.
Soporta 3 escenarios de demostración seleccionables en tiempo real.
"""
from datetime import datetime, date, timezone
from typing import Optional
from sqlalchemy import (
    String, Float, Integer, Boolean, Date, DateTime,
    Text, ForeignKey, JSON, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.database import Base


# ── Catálogo de Productos ─────────────────────────────────────────────────────

class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    sku: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    selling_price: Mapped[float] = mapped_column(Float, nullable=False)
    unit_cost: Mapped[float] = mapped_column(Float, nullable=False)
    shelf_life_days: Mapped[int] = mapped_column(Integer, default=3)
    lead_time_days: Mapped[int] = mapped_column(Integer, default=1)
    min_order_qty: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    sales: Mapped[list["SaleTransaction"]] = relationship(back_populates="product")
    forecasts: Mapped[list["DemandForecast"]] = relationship(back_populates="product")
    model_registry: Mapped[list["ModelRegistry"]] = relationship(back_populates="product")


# ── Configuración de Escenario Activo ────────────────────────────────────────

class ScenarioConfig(Base):
    """
    Tabla singleton (siempre 1 fila) que indica qué escenario de demostración
    está activo. Se usa para filtrar ventas por escenario en tiempo real.

    Escenarios:
      1 = "Corto"   — Dic 2025 a May 2026 (~172 días)
      2 = "Óptimo"  — May 2024 a May 2026 (~730 días, historia completa)
      3 = "Crítico" — Escenario de estrés: alta variabilidad + stock bajo
    """
    __tablename__ = "scenario_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    active_scenario: Mapped[int] = mapped_column(Integer, default=1)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )


# ── Transacciones de Venta ────────────────────────────────────────────────────

class SaleTransaction(Base):
    __tablename__ = "sales_transactions"
    __table_args__ = (
        UniqueConstraint("product_id", "sale_date", "scenario_id", name="uq_product_date_scenario"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scenario_id: Mapped[int] = mapped_column(Integer, nullable=False, default=1, index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)
    sale_date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity_sold: Mapped[float] = mapped_column(Float, nullable=False)
    revenue: Mapped[float] = mapped_column(Float, nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    is_holiday: Mapped[bool] = mapped_column(Boolean, default=False)
    is_payday: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    product: Mapped["Product"] = relationship(back_populates="sales")


# ── Inventario de Insumos ─────────────────────────────────────────────────────

class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    current_stock: Mapped[float] = mapped_column(Float, default=0.0)
    alert_threshold: Mapped[float] = mapped_column(Float, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )


# ── Pronósticos de Demanda ────────────────────────────────────────────────────

class DemandForecast(Base):
    __tablename__ = "demand_forecasts"
    __table_args__ = (UniqueConstraint("product_id", "forecast_date", "model_version", name="uq_forecast"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    forecast_date: Mapped[date] = mapped_column(Date, nullable=False)
    predicted_demand: Mapped[float] = mapped_column(Float, nullable=False)
    lower_bound_90: Mapped[float] = mapped_column(Float, nullable=False)
    upper_bound_90: Mapped[float] = mapped_column(Float, nullable=False)
    mape: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rmse: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    product: Mapped["Product"] = relationship(back_populates="forecasts")


# ── Registro de Modelos ML ────────────────────────────────────────────────────

class ModelRegistry(Base):
    __tablename__ = "model_registry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)
    version_tag: Mapped[str] = mapped_column(String(80), nullable=False)
    training_rows: Mapped[int] = mapped_column(Integer, nullable=False)
    feature_list: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    hyperparameters: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    mape_val: Mapped[float] = mapped_column(Float, default=0.0)
    rmse_val: Mapped[float] = mapped_column(Float, default=0.0)
    mae_val: Mapped[float] = mapped_column(Float, default=0.0)
    storage_path: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    trained_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    product: Mapped["Product"] = relationship(back_populates="model_registry")
