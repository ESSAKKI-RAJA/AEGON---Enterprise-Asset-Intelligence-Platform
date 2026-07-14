from abc import ABC, abstractmethod
from typing import Dict, Any
from app.ml.dto.prediction import PredictionDTO

class IPredictor(ABC):
    """Abstract interface for all prediction services."""
    
    @abstractmethod
    def predict(self, model_name: str, features: Dict[str, Any]) -> PredictionDTO:
        """Returns a standardized PredictionDTO for a given model and feature set."""
        pass
