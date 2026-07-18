from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime

class PredictionDTO(BaseModel):
    """
    Universal prediction output DTO.
    Every prediction must return this format.
    """
    prediction_type: str = Field(..., description="e.g., failure_probability, utilization_forecast")
    prediction_value: float = Field(..., description="The predicted numerical value")
    confidence_score: float = Field(..., description="Statistical confidence (0.0 - 1.0)")
    model_version: str = Field(..., description="Model version used")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    feature_importance: Dict[str, float] = Field(default_factory=dict, description="SHAP values")
    explanation_id: Optional[str] = Field(None, description="UUID referencing global/local explanation logs")
