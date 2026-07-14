import uuid
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import String, Float, ForeignKey, Date, DateTime, Text, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import AuditableBase
from app.models.enums import HealthStatus, FailureRisk

class FeatureStore(AuditableBase):
    """
    Main aggregated features used specifically for ML modeling inputs.
    """
    __tablename__ = "feature_stores"

    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False) # e.g. asset_id
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. ASSET, VENDOR
    features: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False) # Store floats, integers as JSONB

class Prediction(AuditableBase):
    """
    Core AI prediction outcomes details log.
    """
    __tablename__ = "predictions"

    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    target_variable: Mapped[str] = mapped_column(String(100), nullable=False) # e.g., failure_risk, useful_life
    predicted_value: Mapped[str] = mapped_column(String(255), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    prediction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True, nullable=False)

    asset: Mapped["Asset"] = relationship("Asset", back_populates="predictions")
    history: Mapped[List["PredictionHistory"]] = relationship("PredictionHistory", back_populates="prediction", cascade="all, delete-orphan")

class PredictionHistory(AuditableBase):
    """
    Tracks past prediction runs outcomes for accuracy drift auditing.
    """
    __tablename__ = "prediction_histories"

    prediction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("predictions.id", ondelete="CASCADE"), nullable=False, index=True)
    actual_value: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_accurate: Mapped[Optional[bool]] = mapped_column(nullable=True)

    prediction: Mapped["Prediction"] = relationship("Prediction", back_populates="history")

class Recommendation(AuditableBase):
    """
    AI recommended actions (e.g. replace asset, adjust reorder levels).
    """
    __tablename__ = "recommendations"

    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    recommendation_text: Mapped[str] = mapped_column(Text, nullable=False)
    implemented: Mapped[bool] = mapped_column(default=False, nullable=False)

    asset: Mapped["Asset"] = relationship("Asset", back_populates="recommendations")
    history: Mapped[List["RecommendationHistory"]] = relationship("RecommendationHistory", back_populates="recommendation", cascade="all, delete-orphan")

class RecommendationHistory(AuditableBase):
    """
    Audit log tracking recommended outputs status.
    """
    __tablename__ = "recommendation_histories"

    recommendation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("recommendations.id", ondelete="CASCADE"), nullable=False, index=True)
    actioned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    recommendation: Mapped["Recommendation"] = relationship("Recommendation", back_populates="history")

class ModelRegistry(AuditableBase):
    """
    Registry of trained machine learning configurations models.
    """
    __tablename__ = "model_registries"

    model_name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    task_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. REGRESSION, CLASSIFICATION

    versions: Mapped[List["ModelVersion"]] = relationship("ModelVersion", back_populates="model", cascade="all, delete-orphan")

class ModelVersion(AuditableBase):
    """
    ML registry versioning constraints.
    """
    __tablename__ = "model_versions"

    model_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("model_registries.id", ondelete="CASCADE"), nullable=False)
    version_string: Mapped[str] = mapped_column(String(20), nullable=False)
    performance_metrics: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=False, nullable=False)

    model: Mapped["ModelRegistry"] = relationship("ModelRegistry", back_populates="versions")

class TrainingDataset(AuditableBase):
    """
    Keeps audit records of static datasets lists used for AI models.
    """
    __tablename__ = "training_datasets"

    dataset_name: Mapped[str] = mapped_column(String(100), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    records_count: Mapped[int] = mapped_column(nullable=False)

class InferenceLog(AuditableBase):
    """
    Execution records of model predictions calls.
    """
    __tablename__ = "inference_logs"

    model_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("model_versions.id", ondelete="CASCADE"), nullable=False)
    input_data: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    output_data: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    duration_ms: Mapped[int] = mapped_column(nullable=False)

class RiskAssessment(AuditableBase):
    """
    Calculated general institutional hazards or failures risk.
    """
    __tablename__ = "risk_assessments"

    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. ASSET, BUILDING
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

class HealthScore(AuditableBase):
    """
    Standard general asset health calculation metrics.
    """
    __tablename__ = "health_scores"

    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False) # e.g., 0.0 to 100.0
    status: Mapped[HealthStatus] = mapped_column(Enum(HealthStatus), nullable=False)

class FailurePrediction(AuditableBase):
    """
    Specifically forecasts predictive breakdowns of assets.
    """
    __tablename__ = "failure_predictions"

    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    estimated_failure_date: Mapped[date] = mapped_column(Date, nullable=False)
    probability: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[FailureRisk] = mapped_column(Enum(FailureRisk), nullable=False)

class BudgetForecast(AuditableBase):
    """
    Forecasting upcoming budgeting runs.
    """
    __tablename__ = "budget_forecasts"

    fiscal_year: Mapped[int] = mapped_column(nullable=False)
    forecasted_expenditure: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_lower_bound: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_upper_bound: Mapped[float] = mapped_column(Float, nullable=False)

class VendorScore(AuditableBase):
    """
    Tracks performance indicators ratings for vendors.
    """
    __tablename__ = "vendor_scores"

    vendor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False, index=True)
    delivery_rating: Mapped[float] = mapped_column(Float, default=5.0, nullable=False) # 1.0 to 5.0
    quality_rating: Mapped[float] = mapped_column(Float, default=5.0, nullable=False)
    composite_score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)

class AssetUtilization(AuditableBase):
    """
    Tracks assets load/run activity ratios.
    """
    __tablename__ = "asset_utilizations"

    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    utilization_percentage: Mapped[float] = mapped_column(Float, nullable=False) # 0.0 to 100.0
    tracked_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)

class RemainingUsefulLife(AuditableBase):
    """
    AI assessment of assets estimated life left.
    """
    __tablename__ = "remaining_useful_lives"

    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    estimated_remaining_months: Mapped[float] = mapped_column(Float, nullable=False)
