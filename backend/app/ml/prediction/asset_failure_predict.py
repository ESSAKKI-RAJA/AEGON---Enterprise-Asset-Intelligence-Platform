import os
import joblib
import pandas as pd
import numpy as np
from typing import List

from app.ml.dto.ml_predictions import AssetFailurePredictionDTO, SHAPExplanation

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "asset_failure_xgboost.pkl")
EXPLAINER_PATH = os.path.join(MODEL_DIR, "asset_failure_explainer.pkl")

# Cache models in memory
_model = None
_explainer = None

def get_model():
    global _model, _explainer
    if _model is None:
        if os.path.exists(MODEL_PATH) and os.path.exists(EXPLAINER_PATH):
            _model = joblib.load(MODEL_PATH)
            _explainer = joblib.load(EXPLAINER_PATH)
        else:
            raise FileNotFoundError("Model or Explainer not found. Train the model first.")
    return _model, _explainer

def predict_asset_failure(df: pd.DataFrame) -> List[AssetFailurePredictionDTO]:
    """
    Predicts asset failure and provides SHAP explanations.
    """
    model, explainer = get_model()
    
    feature_cols = [
        "age_days", "utilization", "maintenance_freq", 
        "repair_cost", "downtime_hours", "health_score", "environment_factor"
    ]
    
    X = df[feature_cols]
    
    # Predictions
    probs = model.predict_proba(X)[:, 1]
    
    # SHAP values
    shap_values = explainer.shap_values(X)
    
    results = []
    for i, row in df.iterrows():
        prob = float(probs[i])
        
        # Risk Category
        if prob > 0.7:
            risk_category = "HIGH"
            rul = np.random.randint(5, 30)
            business_impact = "High risk of immediate failure. Potential operational halt."
            action = "Schedule emergency maintenance or replacement immediately."
        elif prob > 0.3:
            risk_category = "MEDIUM"
            rul = np.random.randint(31, 180)
            business_impact = "Moderate risk. Could lead to unplanned downtime."
            action = "Schedule preventive maintenance within 30 days."
        else:
            risk_category = "LOW"
            rul = np.random.randint(181, 700)
            business_impact = "Low risk. Normal operations."
            action = "Continue routine monitoring."
            
        # SHAP formatting
        sv = shap_values[i] if isinstance(shap_values, np.ndarray) else shap_values[0][i]
        feature_importance = {feat: float(val) for feat, val in zip(feature_cols, sv)}
        # Get top 3 features contributing to failure risk (positive SHAP values)
        top_features = dict(sorted(feature_importance.items(), key=lambda item: item[1], reverse=True)[:3])
        
        reasoning = f"Failure risk driven by {', '.join([k.replace('_', ' ') for k in top_features.keys()])}."
        
        results.append(AssetFailurePredictionDTO(
            asset_id=str(row["asset_id"]),
            probability=prob,
            risk_category=risk_category,
            remaining_useful_life_days=rul,
            confidence=round(np.random.uniform(0.85, 0.99), 2), # Simulated model confidence
            explanation=SHAPExplanation(
                top_features=top_features,
                reasoning=reasoning
            ),
            business_impact=business_impact,
            recommended_action=action
        ))
        
    return results
