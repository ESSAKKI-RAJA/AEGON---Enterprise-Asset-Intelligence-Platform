import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
import shap
import os
import joblib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.asset import Vendor
from app.core.database import AsyncSessionLocal

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
VENDOR_RISK_MODEL_PATH = os.path.join(MODEL_DIR, "vendor_risk_rf.pkl")
SUPPLIER_RANK_MODEL_PATH = os.path.join(MODEL_DIR, "supplier_rank_gbr.pkl")
VENDOR_EXPLAINER_PATH = os.path.join(MODEL_DIR, "vendor_explainer.pkl")

async def build_procurement_features(session: AsyncSession) -> pd.DataFrame:
    vendors = (await session.execute(select(Vendor))).scalars().all()
    
    data = []
    for vendor in vendors:
        # Simulate historical data
        # Features: order_volume, late_deliveries, defect_rate, cost_variance, average_lead_time
        order_volume = np.random.randint(5, 100)
        late_deliveries = int(order_volume * np.random.uniform(0.01, 0.3))
        defect_rate = np.random.uniform(0.0, 0.15)
        cost_variance = np.random.uniform(-0.1, 0.2)
        avg_lead_time = np.random.uniform(3.0, 45.0)
        
        # Target 1: Vendor Risk (0: Low, 1: Medium, 2: High)
        if late_deliveries / order_volume > 0.2 or defect_rate > 0.1:
            risk = 2
        elif late_deliveries / order_volume > 0.1 or defect_rate > 0.05:
            risk = 1
        else:
            risk = 0
            
        # Target 2: Supplier Score (0-100)
        score = 100 - (late_deliveries/order_volume)*100 - (defect_rate)*200 - (cost_variance)*50
        score = max(0, min(100, score))
        
        data.append({
            "vendor_id": str(vendor.id),
            "order_volume": order_volume,
            "late_deliveries": late_deliveries,
            "defect_rate": defect_rate,
            "cost_variance": cost_variance,
            "avg_lead_time": avg_lead_time,
            "target_risk": risk,
            "target_score": score
        })
        
    return pd.DataFrame(data)

async def train_procurement_models():
    print("Fetching training data for Procurement Intelligence...")
    async with AsyncSessionLocal() as session:
        df = await build_procurement_features(session)
        
    if df.empty:
        return
        
    feature_cols = ["order_volume", "late_deliveries", "defect_rate", "cost_variance", "avg_lead_time"]
    X = df[feature_cols]
    y_risk = df["target_risk"]
    y_score = df["target_score"]
    
    print("Training Vendor Risk Classifier...")
    risk_model = RandomForestClassifier(n_estimators=50, random_state=42)
    risk_model.fit(X, y_risk)
    
    print("Training Supplier Ranking Regressor...")
    rank_model = GradientBoostingRegressor(n_estimators=50, random_state=42)
    rank_model.fit(X, y_score)
    
    print("Building SHAP Explainer...")
    explainer = shap.TreeExplainer(risk_model)
    
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(risk_model, VENDOR_RISK_MODEL_PATH)
    joblib.dump(rank_model, SUPPLIER_RANK_MODEL_PATH)
    joblib.dump(explainer, VENDOR_EXPLAINER_PATH)
    
    print("Procurement Models Trained and Saved.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(train_procurement_models())
