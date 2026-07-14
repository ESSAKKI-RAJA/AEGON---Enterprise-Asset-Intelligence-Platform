import numpy as np
from app.ml.training.pipelines import TrainingPipeline

def generate_synthetic_training_data(n=800):
    """
    Synthetic data generation (stub for actual feature store extraction).
    Returns X, y_failure, y_health.
    """
    np.random.seed(42)
    age_years = np.random.uniform(0, 15, n)
    maintenance_count = np.random.poisson(3, n)
    downtime_hours = np.random.exponential(20, n)
    utilization_rate = np.random.uniform(0, 100, n)
    warranty_active = np.random.choice([0, 1], n)
    maintenance_current = np.random.choice([0, 1], n, p=[0.3, 0.7])

    X = np.column_stack([age_years, maintenance_count, downtime_hours,
                          utilization_rate, warranty_active, maintenance_current])

    failure_score = (
        age_years * 0.08
        + (downtime_hours / 100) * 0.3
        - maintenance_count * 0.05
        - maintenance_current * 0.15
        + np.random.normal(0, 0.1, n)
    )
    failure_prob = 1 / (1 + np.exp(-failure_score))
    y_failure = (failure_prob > 0.5).astype(int)

    health_score = (
        100
        - age_years * 5
        - (downtime_hours / 100) * 20
        + maintenance_current * 10
        + warranty_active * 5
        + np.random.normal(0, 5, n)
    )
    health_score = np.clip(health_score, 0, 100)

    return X, y_failure, health_score

def run_training_pipeline():
    print("Extracting features from Feature Store (Simulated)...")
    X, y_failure, y_health = generate_synthetic_training_data()
    
    pipeline = TrainingPipeline()
    
    print("Training Failure Prediction Model...")
    pipeline.train_classification(
        "failure", 
        X, y_failure, 
        {"n_estimators": 100, "max_depth": 6}
    )
    
    print("Training Asset Health Prediction Model...")
    pipeline.train_regression(
        "health", 
        X, y_health, 
        {"n_estimators": 100, "max_depth": 6}
    )
    
    print("Training complete. Artifacts logged to Model Registry.")

if __name__ == "__main__":
    run_training_pipeline()
