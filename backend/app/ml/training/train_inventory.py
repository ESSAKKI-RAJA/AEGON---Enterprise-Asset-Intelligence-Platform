from prophet import Prophet
import os
import joblib

from app.ml.feature_engineering.inventory_forecast import build_inventory_history_features
from app.core.database import AsyncSessionLocal

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
PROPHET_MODEL_PATH = os.path.join(MODEL_DIR, "inventory_prophet.pkl")

async def train_inventory_model():
    print("Fetching training data for Inventory Forecast...")
    async with AsyncSessionLocal() as session:
        df = await build_inventory_history_features(session)
        
    if df.empty:
        return
        
    # To keep training fast for the entire enterprise, we train a global seasonality model
    # on the aggregated daily demand across all items.
    # Individual item forecasts will scale this pattern based on their base demand.
    
    global_df = df.groupby('ds')['y'].sum().reset_index()
    
    print("Training Global Prophet Model...")
    model = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False)
    model.fit(global_df)
    
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, PROPHET_MODEL_PATH)
    
    print("Prophet Model Trained and Saved.")

if __name__ == "__main__":
    import asyncio
    import logging
    logging.getLogger('cmdstanpy').setLevel(logging.WARNING)
    logging.getLogger('prophet').setLevel(logging.WARNING)
    asyncio.run(train_inventory_model())
