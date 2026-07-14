from enum import Enum
from typing import Dict, Any

class RetrainingStatus(Enum):
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    TRAINING = "training"
    COMPLETED = "completed"
    FAILED = "failed"

class RetrainingWorkflowManager:
    """Manages the approval process for automated continuous retraining."""
    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}

    def request_retraining(self, model_name: str, trigger_reason: str) -> str:
        """Triggers a retraining request requiring human/admin approval."""
        job_id = f"job_{model_name}_{len(self.jobs) + 1}"
        self.jobs[job_id] = {
            "model_name": model_name,
            "trigger_reason": trigger_reason,
            "status": RetrainingStatus.PENDING_APPROVAL.value
        }
        return job_id

    def approve_job(self, job_id: str):
        if job_id in self.jobs and self.jobs[job_id]["status"] == RetrainingStatus.PENDING_APPROVAL.value:
            self.jobs[job_id]["status"] = RetrainingStatus.APPROVED.value
            # In real system, this would push a message to RabbitMQ/Kafka to start the TrainingOrchestrator
            return True
        return False

workflow_manager = RetrainingWorkflowManager()
