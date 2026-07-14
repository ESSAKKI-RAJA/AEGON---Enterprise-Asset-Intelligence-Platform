from typing import Dict, Any
from datetime import datetime
import json
import os

class MLflowAdapter:
    """
    Simulates MLflow tracking server locally.
    Records experiments, metrics, and manages artifact paths.
    """
    def __init__(self, registry_path: str = "mlruns"):
        self.registry_path = os.path.join(os.getcwd(), registry_path)
        if not os.path.exists(self.registry_path):
            os.makedirs(self.registry_path, exist_ok=True)

    def get_latest_model(self, name: str):
        # Stub
        return None

    def log_model(self, name: str, metrics: Dict[str, Any], params: Dict[str, Any]):
        """Logs a model version."""
        timestamp = datetime.utcnow().isoformat().replace(":", "-")
        run_dir = os.path.join(self.registry_path, f"{name}_{timestamp}")
        os.makedirs(run_dir, exist_ok=True)
        
        metadata = {
            "model_name": name,
            "training_date": timestamp,
            "metrics": metrics,
            "hyperparameters": params,
            "stage": "development",
            "owner": "automated_pipeline",
            "framework": "scikit-learn"
        }
        
        with open(os.path.join(run_dir, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)

mlflow_client = MLflowAdapter()
