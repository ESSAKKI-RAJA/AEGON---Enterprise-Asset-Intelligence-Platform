import os
import joblib
import pandas as pd
import numpy as np
from typing import List

from app.ml.dto.ml_predictions import SHAPExplanation
from pydantic import BaseModel

class MaintenancePredictionDTO(BaseModel):
    asset_id: str
    estimated_maintenance_cost: float
    recommended_priority: str
    priority_confidence: float
    explanation: SHAPExplanation

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
MAINT_COST_MODEL_PATH = os.path.join(MODEL_DIR, "maint_cost_rf.pkl")
MAINT_COST_EXPLAINER = os.path.join(MODEL_DIR, "maint_cost_explainer.pkl")
MAINT_PRIORITY_MODEL_PATH = os.path.join(MODEL_DIR, "maint_priority_rf.pkl")

_cost_model = None
_priority_model = None
_explainer = None

def get_models():
    global _cost_model, _priority_model, _explainer
    if _cost_model is None:
        if os.path.exists(MAINT_COST_MODEL_PATH) and os.path.exists(MAINT_PRIORITY_MODEL_PATH):
            _cost_model = joblib.load(MAINT_COST_MODEL_PATH)
            _priority_model = joblib.load(MAINT_PRIORITY_MODEL_PATH)
            _explainer = joblib.load(MAINT_COST_EXPLAINER)
        else:
            raise FileNotFoundError("Maintenance models not found.")
    return _cost_model, _priority_model, _explainer

def predict_maintenance(df: pd.DataFrame) -> List[MaintenancePredictionDTO]:
    cost_model, priority_model, explainer = get_models()
    
    feature_cols = ["health_score", "purchase_cost", "category_id"]
    X = df[feature_cols]
    
    cost_preds = cost_model.predict(X)
    priority_preds = priority_model.predict(X)
    priority_probs = priority_model.predict_proba(X)
    
    shap_values = explainer.shap_values(X)
    
    priority_map = {0: "LOW", 1: "MEDIUM", 2: "HIGH", 3: "CRITICAL"}
    
    results = []
    for i, row in df.iterrows():
        p_class = int(priority_preds[i])
        p_prob = float(np.max(priority_probs[i]))
        
        sv = shap_values[i] if isinstance(shap_values, np.ndarray) else shap_values[0][i]
        feature_importance = {feat: float(val) for feat, val in zip(feature_cols, sv)}
        top_features = dict(sorted(feature_importance.items(), key=lambda item: abs(item[1]), reverse=True)[:2])
        
        reasoning = f"Cost influenced by {', '.join([k.replace('_', ' ') for k in top_features.keys()])}."
        
        results.append(MaintenancePredictionDTO(
            asset_id=str(row["asset_id"]),
            estimated_maintenance_cost=round(float(cost_preds[i]), 2),
            recommended_priority=priority_map.get(p_class, "LOW"),
            priority_confidence=round(p_prob, 2),
            explanation=SHAPExplanation(
                top_features=top_features,
                reasoning=reasoning
            )
        ))
    return results
