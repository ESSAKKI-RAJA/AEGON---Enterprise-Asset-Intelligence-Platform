from typing import Dict, Any
from app.ml.interfaces.trainer import ITrainer
from app.ml.training.cross_validation import CrossValidator
from app.ml.training.hyperparameter_search import HyperparameterSearch
import logging

logger = logging.getLogger(__name__)

class TrainingOrchestrator(ITrainer):
    """
    Coordinates Data Fetching, Hyperparameter Search, and CV.
    """
    def __init__(self, registry):
        self.registry = registry

    def train(self, experiment_name: str, X: Any, y: Any, params: Dict[str, Any]):
        logger.info(f"Starting training for experiment: {experiment_name}")
        
        # 1. Hyperparameter Search
        search_space = params.get("search_space", {})
        if search_space:
            searcher = HyperparameterSearch(search_space)
            best_params = searcher.search(params.get("model_type", "rf"), X, y)
            logger.info(f"Found best params: {best_params}")
        
        # 2. Cross Validation
        cv = CrossValidator()
        cv_metrics = cv.validate("dummy_model", X, y)
        
        # 3. Model Registration (simulated via MLflowAdapter inside registry)
        if cv_metrics["passed_validation"]:
            self.registry.log_model(
                name=experiment_name,
                metrics=cv_metrics,
                params=best_params["best_params"] if search_space else params
            )
            logger.info("Training passed validation and model registered.")
        else:
            logger.warning("Model failed cross-validation constraints.")
