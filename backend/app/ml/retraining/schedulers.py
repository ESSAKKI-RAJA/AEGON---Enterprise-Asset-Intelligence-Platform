from app.ml.retraining.workflows import workflow_manager
import logging

logger = logging.getLogger(__name__)

class RetrainingScheduler:
    """
    Subscribes to Drift events and triggers the Retraining Workflow.
    """
    def __init__(self):
        pass

    async def on_drift_detected(self, drift_event: dict):
        """Event handler for Data or Concept Drift."""
        model_name = drift_event.get("model_name", "unknown")
        severity = drift_event.get("severity", "LOW")
        
        if severity in ["HIGH", "CRITICAL"]:
            logger.warning(f"Drift detected for {model_name}. Requesting retraining.")
            job_id = workflow_manager.request_retraining(model_name, trigger_reason="drift_detected")
            logger.info(f"Retraining job {job_id} created and pending approval.")

    async def schedule_periodic_retraining(self, model_name: str):
        """Cron-style handler for weekly/monthly scheduled retraining."""
        job_id = workflow_manager.request_retraining(model_name, trigger_reason="scheduled_maintenance")
        # For scheduled maintenance, maybe auto-approve
        workflow_manager.approve_job(job_id)
        
retraining_scheduler = RetrainingScheduler()
