import os
import joblib
import pandas as pd
import numpy as np
from typing import List
from pydantic import BaseModel

from app.ml.dto.ml_predictions import SHAPExplanation

class ProcurementForecastDTO(BaseModel):
    vendor_id: str
    risk_level: str
    supplier_score: float
    recommended_action: str
    explanation: SHAPExplanation

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
VENDOR_RISK_MODEL_PATH = os.path.join(MODEL_DIR, "vendor_risk_rf.pkl")
SUPPLIER_RANK_MODEL_PATH = os.path.join(MODEL_DIR, "supplier_rank_gbr.pkl")
VENDOR_EXPLAINER_PATH = os.path.join(MODEL_DIR, "vendor_explainer.pkl")

_risk_model = None
_rank_model = None
_explainer = None

def get_procurement_models():
    global _risk_model, _rank_model, _explainer
    if _risk_model is None:
        if os.path.exists(VENDOR_RISK_MODEL_PATH):
            _risk_model = joblib.load(VENDOR_RISK_MODEL_PATH)
            _rank_model = joblib.load(SUPPLIER_RANK_MODEL_PATH)
            _explainer = joblib.load(VENDOR_EXPLAINER_PATH)
        else:
            raise FileNotFoundError("Procurement models not found.")
    return _risk_model, _rank_model, _explainer

def predict_procurement(df: pd.DataFrame) -> List[ProcurementForecastDTO]:
    risk_model, rank_model, explainer = get_procurement_models()
    
    feature_cols = ["order_volume", "late_deliveries", "defect_rate", "cost_variance", "avg_lead_time"]
    X = df[feature_cols]
    
    risk_preds = risk_model.predict(X)
    score_preds = rank_model.predict(X)
    shap_values = explainer.shap_values(X)
    
    risk_map = {0: "LOW", 1: "MEDIUM", 2: "HIGH"}
    
    results = []
    for i, row in df.iterrows():
        p_class = int(risk_preds[i])
        score = float(score_preds[i])
        
        sv = shap_values[i] if isinstance(shap_values, np.ndarray) else shap_values[0][i]
        feature_importance = {feat: float(val) for feat, val in zip(feature_cols, sv)}
        top_features = dict(sorted(feature_importance.items(), key=lambda item: abs(item[1]), reverse=True)[:2])
        
        reasoning = f"Supplier risk influenced by {', '.join([k.replace('_', ' ') for k in top_features.keys()])}."
        
        action = "Maintain preferred supplier status."
        if p_class == 2:
            action = "Urgent: Source alternative suppliers."
        elif p_class == 1:
            action = "Monitor closely; request performance improvement plan."
            
        results.append(ProcurementForecastDTO(
            vendor_id=str(row["vendor_id"]),
            risk_level=risk_map.get(p_class, "LOW"),
            supplier_score=round(score, 1),
            recommended_action=action,
            explanation=SHAPExplanation(
                top_features=top_features,
                reasoning=reasoning
            )
        ))
    return results
