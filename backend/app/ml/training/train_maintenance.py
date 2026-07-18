import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
import shap
import os
import joblib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.asset import Asset
from app.core.database import AsyncSessionLocal

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
MAINT_COST_MODEL_PATH = os.path.join(MODEL_DIR, "maint_cost_rf.pkl")
MAINT_COST_EXPLAINER = os.path.join(MODEL_DIR, "maint_cost_explainer.pkl")
MAINT_PRIORITY_MODEL_PATH = os.path.join(MODEL_DIR, "maint_priority_rf.pkl")

async def build_maintenance_features(session: AsyncSession) -> pd.DataFrame:
    assets = (await session.execute(select(Asset))).scalars().all()
    
    data = []
    for asset in assets:
        # We simulate historical work order data for training
        base_cost = asset.purchase_cost * 0.05 if asset.purchase_cost else 500.0
        
        # Priority mapping: 0: Low, 1: Medium, 2: High, 3: Critical
        # Cost is influenced by age and health
        health = asset.health_score if asset.health_score else 80.0
        
        priority = 0
        if health < 40:
            priority = 3
            cost = base_cost * np.random.uniform(2.0, 5.0)
        elif health < 60:
            priority = 2
            cost = base_cost * np.random.uniform(1.2, 2.0)
        elif health < 80:
            priority = 1
            cost = base_cost * np.random.uniform(0.8, 1.2)
        else:
            priority = 0
            cost = base_cost * np.random.uniform(0.5, 0.8)
            
        data.append({
            "asset_id": str(asset.id),
            "health_score": health,
            "purchase_cost": asset.purchase_cost if asset.purchase_cost else 10000.0,
            "category_id": hash(str(asset.category_id)) % 100, # Categorical encoding
            "target_cost": cost,
            "target_priority": priority
        })
        
    return pd.DataFrame(data)

async def train_maintenance_models():
    print("Fetching training data for Maintenance Prediction Engine...")
    async with AsyncSessionLocal() as session:
        df = await build_maintenance_features(session)
        
    if df.empty:
        return
        
    feature_cols = ["health_score", "purchase_cost", "category_id"]
    X = df[feature_cols]
    y_cost = df["target_cost"]
    y_priority = df["target_priority"]
    
    print("Training Random Forest Cost Regressor...")
    cost_model = RandomForestRegressor(n_estimators=50, random_state=42)
    cost_model.fit(X, y_cost)
    
    print("Training Random Forest Priority Classifier...")
    priority_model = RandomForestClassifier(n_estimators=50, random_state=42)
    priority_model.fit(X, y_priority)
    
    print("Building SHAP Explainer for Cost...")
    # TreeExplainer is fast for RF
    explainer = shap.TreeExplainer(cost_model)
    
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(cost_model, MAINT_COST_MODEL_PATH)
    joblib.dump(explainer, MAINT_COST_EXPLAINER)
    joblib.dump(priority_model, MAINT_PRIORITY_MODEL_PATH)
    
    print("Maintenance Models Trained and Saved.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(train_maintenance_models())
