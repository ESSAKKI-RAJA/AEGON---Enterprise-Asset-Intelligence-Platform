from typing import Dict, Any
import time

from app.ml.interfaces.predictor import IPredictor
from app.ml.dto.prediction import PredictionDTO
from app.ml.inference.real_time import real_time_predictor
from app.ml.explainability.engine import explainability_engine
from app.ml.monitoring.performance import performance_monitor
from app.ml.feature_store.online_store import online_store

class EnterpriseMLGateway(IPredictor):
    """
    The Single Public Entry Point for the entire ML Platform.
    No other layer may access models, registry, or pipelines directly.
    """
    def __init__(self):
        pass

    def predict(self, model_name: str, features: Dict[str, Any] = None, entity_id: str = None) -> PredictionDTO:
        start_time = time.time()
        
        # 1. Feature Retrieval if not explicitly provided
        if not features and entity_id:
            # Assuming we need a default set of feature names based on model
            features = online_store.get_feature_vector(entity_id, ["f1", "f2"])
        
        if not features:
            features = {}

        # 2. Inference Routing
        prediction_dto = real_time_predictor.predict(model_name, features)

        # 3. Explainability Hook
        explanation = explainability_engine.explain_local(
            model=model_name, 
            feature_vector=list(features.values()), 
            feature_names=list(features.keys())
        )
        prediction_dto.feature_importance = explanation["feature_importance"]
        prediction_dto.explanation_id = explanation["explanation_id"]

        # 4. Performance Monitoring
        latency_ms = (time.time() - start_time) * 1000
        performance_monitor.log_inference_metrics(model_name, latency_ms, memory_mb=0)

        return prediction_dto

ml_gateway = EnterpriseMLGateway()
