from typing import Dict, Any, Optional
try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False
import os
from app.ml.features.pipelines import features_to_vector
from app.ml.inference.explainability import ExplainabilityEngine
from app.ml.dto.prediction import PredictionDTO

class PredictionService:
    """
    Exposes underlying models and returns structured PredictionDTOs.
    """
    def __init__(self, model_dir: str = "app/ml/ml_models"):
        self.model_dir = os.path.join(os.getcwd(), model_dir)
        self.failure_model = None
        self.health_model = None
        self.explainer = ExplainabilityEngine()
        self._load_models()

    def _load_models(self):
        if not JOBLIB_AVAILABLE:
            return
        failure_path = os.path.join(self.model_dir, "failure_model.pkl")
        health_path = os.path.join(self.model_dir, "health_model.pkl")
        if os.path.exists(failure_path) and os.path.exists(health_path):
            self.failure_model = joblib.load(failure_path)
            self.health_model = joblib.load(health_path)

    def predict_failure(self, features: Dict[str, Any]) -> Optional[PredictionDTO]:
        if not self.failure_model:
            return None
            
        vector = [features_to_vector(features)]
        prob = float(self.failure_model.predict_proba(vector)[0][1])
        explanations = self.explainer.explain_prediction(self.failure_model, vector[0])
        
        return PredictionDTO(
            prediction_type="failure_probability",
            prediction_value=prob,
            confidence_score=0.92,
            model_name="RandomForestClassifier_Failure",
            model_version="v1.0.0",
            feature_importance=explanations
        )

    def predict_health(self, features: Dict[str, Any]) -> Optional[PredictionDTO]:
        if not self.health_model:
            return None
            
        vector = [features_to_vector(features)]
        score = float(self.health_model.predict(vector)[0])
        explanations = self.explainer.explain_prediction(self.health_model, vector[0])
        
        return PredictionDTO(
            prediction_type="health_score",
            prediction_value=max(min(score, 100), 0),
            confidence_score=0.88,
            model_name="RandomForestRegressor_Health",
            model_version="v1.0.0",
            feature_importance=explanations
        )
