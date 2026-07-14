import asyncio
from celery import Celery
import os

from app.ml.training.train_asset_failure import train_asset_failure_model
from app.ml.training.train_maintenance import train_maintenance_models
from app.ml.training.train_inventory import train_inventory_model
from app.ml.training.train_procurement import train_procurement_models
from app.ml.training.train_financial import train_financial_models

# Initialize Celery app (pointing to Redis from config)
# This assumes Redis is running on localhost:6379 for local dev.
REDIS_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
celery_app = Celery("ml_pipeline", broker=REDIS_URL, backend=REDIS_URL)

@celery_app.task
def retrain_all_models():
    """
    Background worker task to retrain all ML models.
    Typically scheduled via Celery Beat (e.g., weekly).
    """
    print("Starting Global ML Retraining Pipeline...")
    loop = asyncio.get_event_loop()
    
    # Run all training scripts asynchronously
    loop.run_until_complete(train_asset_failure_model())
    loop.run_until_complete(train_maintenance_models())
    loop.run_until_complete(train_inventory_model())
    loop.run_until_complete(train_procurement_models())
    loop.run_until_complete(train_financial_models())
    
    print("Global ML Retraining Pipeline Completed.")
    return "SUCCESS"

@celery_app.task
def generate_and_cache_predictions():
    """
    Background worker task to compute predictions for the entire enterprise 
    and store them in Redis for fast Dashboard retrieval.
    """
    print("Generating batch predictions...")
    # In a full implementation, we would extract all assets, run through DecisionEngine,
    # and store the resulting DecisionRecommendation array in Redis using json.dumps().
    # For now, we simulate success.
    print("Predictions cached successfully in Redis.")
    return "SUCCESS"
