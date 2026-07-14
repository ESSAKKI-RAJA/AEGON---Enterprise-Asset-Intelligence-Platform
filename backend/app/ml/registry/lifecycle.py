from enum import Enum
from typing import Dict, Any

class ModelStage(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"
    ROLLBACK = "rollback"

class ModelLifecycleManager:
    """
    Manages the promotion and rollback of models through explicit stages.
    """
    def __init__(self):
        self.registry: Dict[str, Dict[str, Any]] = {} # model_name -> {version -> details}

    def promote_model(self, model_name: str, version: str, target_stage: ModelStage):
        """Promotes a model to a target stage (e.g., Staging -> Production)."""
        if model_name in self.registry and version in self.registry[model_name]:
            self.registry[model_name][version]["stage"] = target_stage.value
            return True
        return False

    def rollback_model(self, model_name: str) -> str:
        """Rolls back Production to the previous version."""
        # Simulated rollback logic
        return "v1.0.0"

lifecycle_manager = ModelLifecycleManager()
