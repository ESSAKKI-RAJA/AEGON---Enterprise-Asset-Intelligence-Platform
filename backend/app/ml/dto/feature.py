from pydantic import BaseModel, Field
from typing import Dict, Any
from datetime import datetime

class FeatureDTO(BaseModel):
    """
    Standardized Feature format passing between the Store and Pipelines.
    """
    feature_name: str
    description: str
    owner: str
    source_business_service: str
    refresh_frequency: str
    data_type: str
    version: str = "1.0.0"
    created_date: datetime = Field(default_factory=datetime.utcnow)
    modified_date: datetime = Field(default_factory=datetime.utcnow)
    validation_rules: Dict[str, Any] = Field(default_factory=dict)
