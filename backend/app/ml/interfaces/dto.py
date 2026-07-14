from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

class PredictionDTO(BaseModel):
    """
    Standard Prediction DTO returned by all ML Gateway endpoints.
    Every future AI engine should consume this DTO.
    """
    prediction_type: str = Field(..., description="E.g., 'failure_probability', 'health_score'")
    prediction_value: float = Field(..., description="The predicted numerical value")
    confidence_score: float = Field(..., description="Confidence score from 0.0 to 1.0")
    model_name: str = Field(..., description="Name of the model used")
    model_version: str = Field(..., description="Version of the model used")
    feature_importance: Dict[str, float] = Field(default_factory=dict, description="SHAP or relative importance scores")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Time of prediction")
    explanation_reference: Optional[str] = Field(None, description="Optional link or ID for extended explainability data")
