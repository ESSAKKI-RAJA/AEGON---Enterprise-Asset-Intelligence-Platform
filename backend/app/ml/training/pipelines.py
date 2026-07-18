import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import joblib
import os
from typing import Dict, Any

from app.ml.registry.mlflow_adapter import mlflow_client

class TrainingPipeline:
    """
    Automated training pipelines with cross-validation and evaluation.
    Integrated with the Model Registry (MLflowAdapter).
    """
    def __init__(self, model_dir: str = "app/ml/ml_models"):
        self.model_dir = os.path.join(os.getcwd(), model_dir)
        os.makedirs(self.model_dir, exist_ok=True)

    def _split_data(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2):
        # Extremely simplified split for example purposes
        split_idx = int(len(X) * (1 - test_size))
        return X[:split_idx], X[split_idx:], y[:split_idx], y[split_idx:]

    def train_classification(self, experiment_name: str, X: np.ndarray, y: np.ndarray, params: Dict[str, Any]):
        mlflow_client.start_run(experiment_name)
        for k, v in params.items():
            mlflow_client.log_param(k, v)
            
        X_train, X_test, y_train, y_test = self._split_data(X, y)
        
        model = RandomForestClassifier(**params, random_state=42)
        model.fit(X_train, y_train)
        
        acc = model.score(X_test, y_test)
        mlflow_client.log_metric("accuracy", float(acc))
        
        # Save model
        model_path = os.path.join(self.model_dir, f"{experiment_name}_model.pkl")
        joblib.dump(model, model_path)
        mlflow_client.log_model(experiment_name, model_path)
        
        mlflow_client.end_run()
        return model, {"accuracy": acc}

    def train_regression(self, experiment_name: str, X: np.ndarray, y: np.ndarray, params: Dict[str, Any]):
        mlflow_client.start_run(experiment_name)
        for k, v in params.items():
            mlflow_client.log_param(k, v)
            
        X_train, X_test, y_train, y_test = self._split_data(X, y)
        
        model = RandomForestRegressor(**params, random_state=42)
        model.fit(X_train, y_train)
        
        r2 = model.score(X_test, y_test)
        mlflow_client.log_metric("r2_score", float(r2))
        
        # Save model
        model_path = os.path.join(self.model_dir, f"{experiment_name}_model.pkl")
        joblib.dump(model, model_path)
        mlflow_client.log_model(experiment_name, model_path)
        
        mlflow_client.end_run()
        return model, {"r2_score": r2}
