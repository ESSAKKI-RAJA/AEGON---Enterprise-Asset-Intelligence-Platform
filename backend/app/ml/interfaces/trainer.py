from abc import ABC, abstractmethod
from typing import Dict, Any
import numpy as np

class ITrainer(ABC):
    """Abstract interface for model training pipelines."""
    
    @abstractmethod
    def train(self, experiment_name: str, X: np.ndarray, y: np.ndarray, params: Dict[str, Any]):
        """Executes a training run."""
        pass
