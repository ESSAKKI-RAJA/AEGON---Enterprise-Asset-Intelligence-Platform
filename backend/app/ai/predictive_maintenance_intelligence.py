from typing import Dict, Any
from app.ml.dto.prediction import PredictionDTO

def get_predictive_maintenance_schedule(failure_prediction: PredictionDTO) -> Dict[str, Any]:
    # Extremely simplified logic based on prediction value
    days_to_failure = max(1, int((1.0 - failure_prediction.prediction_value) * 100))
    
    return {
        "recommended_schedule": f"Within {days_to_failure} days",
        "estimated_downtime_hours": 4,
        "suggested_technician_level": "Senior" if failure_prediction.prediction_value > 0.8 else "Standard",
        "source_prediction_confidence": failure_prediction.confidence_score
    }
