from typing import Dict, Any

class OnlineFeatureStore:
    """
    Simulates a low-latency Redis/Memcached online feature store for real-time inference.
    """
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get_feature_vector(self, entity_id: str, feature_names: list[str]) -> Dict[str, Any]:
        """Retrieves real-time features for an entity."""
        # For missing online features, we would normally trigger an on-the-fly computation
        # through the Feature Pipelines, but here we assume they are pre-computed/cached.
        cached = self._cache.get(entity_id, {})
        return {f_name: cached.get(f_name) for f_name in feature_names}

    def write_features(self, entity_id: str, features: Dict[str, Any]):
        """Writes computed features to the online cache."""
        if entity_id not in self._cache:
            self._cache[entity_id] = {}
        self._cache[entity_id].update(features)

online_store = OnlineFeatureStore()
