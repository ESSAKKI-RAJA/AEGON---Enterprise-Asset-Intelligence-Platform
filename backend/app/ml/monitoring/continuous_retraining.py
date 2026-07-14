from app.core.events import DomainEvent
from app.ml.monitoring.drift import ModelDriftEvent
from app.ml.train_models import run_training_pipeline
import asyncio

class ContinuousRetrainingOrchestrator:
    """
    Listens for drift events and triggers retraining pipelines.
    Acts as the glue between ML Monitoring and ML Training.
    """
    def __init__(self):
        self.retraining_lock = asyncio.Lock()

    async def handle_drift_event(self, event: DomainEvent):
        """Subscriber callback for ModelDriftEvent."""
        if isinstance(event, ModelDriftEvent):
            print(f"🔄 Retraining Orchestrator received drift event for {event.model_name} (Score: {event.drift_score})")
            
            # Prevent multiple simultaneous retraining triggers
            if self.retraining_lock.locked():
                print("⏳ Retraining already in progress. Skipping.")
                return
                
            async with self.retraining_lock:
                print(f"🚀 Triggering background retraining for {event.model_name}...")
                # In production, this would dispatch a Celery/Kafka task
                # We simulate it with asyncio.to_thread
                await asyncio.to_thread(run_training_pipeline)
                print(f"✅ Retraining for {event.model_name} complete.")
