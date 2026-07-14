from abc import ABC, abstractmethod
from typing import Dict, Any

class IFeaturePipeline(ABC):
    """Abstract interface for feature pipelines."""
    
    @abstractmethod
    async def generate_features(self, entity: Any) -> Dict[str, Any]:
        """Turns a raw entity into a dictionary of features."""
        pass
