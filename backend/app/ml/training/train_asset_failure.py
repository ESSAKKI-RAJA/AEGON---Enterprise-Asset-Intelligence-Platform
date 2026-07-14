import pandas as pd
import xgboost as xgb
import shap
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
from sqlalchemy.ext.asyncio import AsyncSession

from app.ml.feature_engineering.asset_failure import build_asset_failure_features
from app.core.database import AsyncSessionLocal

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "asset_failure_xgboost.pkl")
EXPLAINER_PATH = os.path.join(MODEL_DIR, "asset_failure_explainer.pkl")

async def train_asset_failure_model():
    """
    Trains an XGBoost model for Asset Failure Prediction.
    Saves the model and SHAP explainer.
    """
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    print("Fetching training data...")
    async with AsyncSessionLocal() as session:
        df = await build_asset_failure_features(session)
        
    if df.empty or len(df) < 50:
        print("Not enough data to train model.")
        return
        
    # We might have highly imbalanced data. XGBoost handles this well with scale_pos_weight.
    # Features
    feature_cols = [
        "age_days", "utilization", "maintenance_freq", 
        "repair_cost", "downtime_hours", "health_score", "environment_factor"
    ]
    
    X = df[feature_cols]
    y = df["has_failed"]
    
    # Check if we have both classes
    if len(y.unique()) < 2:
        print("Dataset only contains one class. Cannot train classification model. Injecting synthetic data for demonstration.")
        # Inject synthetic failure for MSBA demo if database is too clean
        synthetic_failed = X.copy().sample(n=min(20, len(X)))
        synthetic_failed['health_score'] = synthetic_failed['health_score'] * np.random.uniform(0.1, 0.4)
        synthetic_failed['downtime_hours'] = synthetic_failed['downtime_hours'] + 100
        
        y = pd.concat([y, pd.Series([1]*len(synthetic_failed))])
        X = pd.concat([X, synthetic_failed])
        
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Calculate scale_pos_weight
    neg_count = sum(y_train == 0)
    pos_count = sum(y_train == 1)
    scale_weight = neg_count / max(1, pos_count)
    
    print("Training XGBoost...")
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        scale_pos_weight=scale_weight,
        random_state=42,
        eval_metric='auc'
    )
    
    model.fit(X_train, y_train)
    
    print("Evaluating Model...")
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]
    
    precision = precision_score(y_test, preds, zero_division=0)
    recall = recall_score(y_test, preds, zero_division=0)
    f1 = f1_score(y_test, preds, zero_division=0)
    try:
        roc_auc = roc_auc_score(y_test, probs)
    except ValueError:
        roc_auc = 0.5
    
    print(f"Metrics -> Precision: {precision:.2f}, Recall: {recall:.2f}, F1: {f1:.2f}, ROC AUC: {roc_auc:.2f}")
    
    print("Building SHAP Explainer...")
    explainer = shap.TreeExplainer(model)
    
    print("Saving Models to disk...")
    joblib.dump(model, MODEL_PATH)
    joblib.dump(explainer, EXPLAINER_PATH)
    
    print("Training Complete.")
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc
    }

if __name__ == "__main__":
    import asyncio
    import numpy as np # Ensure np is available for synthetic data injection if needed
    asyncio.run(train_asset_failure_model())
