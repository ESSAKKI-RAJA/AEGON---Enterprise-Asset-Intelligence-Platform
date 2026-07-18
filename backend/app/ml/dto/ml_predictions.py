from pydantic import BaseModel
from typing import Dict

class SHAPExplanation(BaseModel):
    top_features: Dict[str, float]
    reasoning: str

class AssetFailurePredictionDTO(BaseModel):
    asset_id: str
    probability: float
    risk_category: str
    remaining_useful_life_days: int
    confidence: float
    explanation: SHAPExplanation
    business_impact: str
    recommended_action: str
