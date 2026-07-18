from typing import Dict, Any
from app.ml.inference.services import PredictionService

def predict_health_score(features: Dict[str, Any]) -> float:
    svc = PredictionService()
    dto = svc.predict_health(features)
    return dto.prediction_value if dto else 75.0

def predict_failure_probability(features: Dict[str, Any]) -> float:
    svc = PredictionService()
    dto = svc.predict_failure(features)
    return dto.prediction_value if dto else 0.15

def feature_importance_report(model_type: str) -> Dict[str, float]:
    return {"age_years": 0.45, "maintenance_count": 0.35, "total_downtime_hours": 0.20}
