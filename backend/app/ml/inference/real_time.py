from typing import Dict, Any
from app.ml.dto.prediction import PredictionDTO
from app.ml.inference.services import PredictionService

class RealTimePredictor:
    """Handles synchronous, low-latency prediction requests."""
    def __init__(self):
        self.service = PredictionService()

    def predict(self, model_name: str, features: Dict[str, Any]) -> PredictionDTO:
        if model_name == "failure":
            return self.service.predict_failure(features)
        elif model_name == "health":
            return self.service.predict_health(features)
        raise ValueError(f"Unknown real-time model: {model_name}")

real_time_predictor = RealTimePredictor()
