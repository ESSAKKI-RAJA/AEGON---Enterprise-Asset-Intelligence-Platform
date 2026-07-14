from typing import Dict, Any, List
from app.ml.dto.feature import FeatureDTO

class FeatureRegistry:
    """
    Central repository for feature definitions and metadata.
    """
    def __init__(self):
        self._registered_features: Dict[str, FeatureDTO] = {}

    def register_feature(self, feature: FeatureDTO):
        """Registers a new feature definition."""
        self._registered_features[feature.feature_name] = feature

    def get_feature(self, feature_name: str) -> FeatureDTO:
        """Retrieves a feature definition."""
        if feature_name not in self._registered_features:
            raise ValueError(f"Feature {feature_name} not found in Registry.")
        return self._registered_features[feature_name]

    def list_features(self, source_service: str = None) -> List[FeatureDTO]:
        """Lists registered features, optionally filtered by source service."""
        if source_service:
            return [f for f in self._registered_features.values() if f.source_business_service == source_service]
        return list(self._registered_features.values())

feature_registry = FeatureRegistry()
