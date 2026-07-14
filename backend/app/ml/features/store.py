from typing import Dict, Any, List, Optional
import time

class FeatureStore:
    """
    Enterprise Feature Store for registering, versioning, and retrieving features.
    In production, this would bridge to an Online Store (Redis) and Offline Store (S3/Data Warehouse).
    For now, it acts as an abstraction layer holding features in memory.
    """
    def __init__(self):
        self._online_store: Dict[str, Dict[str, Any]] = {}
        self._feature_metadata: Dict[str, Any] = {}

    def register_feature_group(self, name: str, version: str, description: str, features: List[str]):
        """Registers a group of features with the store."""
        self._feature_metadata[name] = {
            "version": version,
            "description": description,
            "features": features,
            "registered_at": time.time()
        }

    def write_features(self, entity_id: str, feature_group: str, features: Dict[str, Any]):
        """Writes features to the online store for low-latency retrieval."""
        if feature_group not in self._feature_metadata:
            raise ValueError(f"Feature group {feature_group} not registered.")
            
        key = f"{feature_group}:{entity_id}"
        self._online_store[key] = features

    def get_online_features(self, entity_id: str, feature_group: str) -> Optional[Dict[str, Any]]:
        """Retrieves low-latency features for real-time inference."""
        key = f"{feature_group}:{entity_id}"
        return self._online_store.get(key)
        
    def get_offline_features(self, entity_ids: List[str], feature_group: str) -> List[Dict[str, Any]]:
        """Retrieves a batch of features for training (mocked here)."""
        return [self.get_online_features(eid, feature_group) for eid in entity_ids if self.get_online_features(eid, feature_group)]

# Global instance for simplicity
feature_store = FeatureStore()
