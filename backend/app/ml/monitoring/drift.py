from typing import Dict, Any, List
import numpy as np
from app.core.events import EventDispatcher, DomainEvent
import uuid

class ModelDriftEvent(DomainEvent):
    def __init__(self, model_name: str, drift_score: float, **kwargs):
        super().__init__(**kwargs)
        self.model_name = model_name
        self.drift_score = drift_score

class DriftDetector:
    """
    Monitors inference payloads for Data Drift and Concept Drift.
    """
    def __init__(self, event_dispatcher: EventDispatcher):
        self.dispatcher = event_dispatcher
        # In a real app, reference_data would be pulled from the Feature Store 
        # based on the dataset the model was trained on.
        self.reference_mean = [5.0, 3.0, 15.0, 50.0, 0.5, 0.5]
        self.drift_threshold = 2.0 # Standard deviations

    async def check_data_drift(self, model_name: str, incoming_batch: List[List[float]]):
        """
        Simple heuristic: check if the incoming batch mean deviates significantly
        from the reference mean.
        """
        if not incoming_batch:
            return
            
        batch_array = np.array(incoming_batch)
        batch_mean = np.mean(batch_array, axis=0)
        
        # Calculate a naive drift score (e.g., Euclidean distance of means)
        drift_score = np.linalg.norm(batch_mean - self.reference_mean)
        
        if drift_score > self.drift_threshold:
            print(f"⚠️ Data drift detected for {model_name}! Score: {drift_score}")
            await self.dispatcher.publish(ModelDriftEvent(model_name, float(drift_score)))
        else:
            print(f"✅ No significant drift for {model_name}. Score: {drift_score}")
