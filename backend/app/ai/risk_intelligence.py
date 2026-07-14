from typing import Dict, Any
from app.ml.dto.prediction import PredictionDTO

def evaluate_enterprise_risk(failure_prediction: PredictionDTO, financial_kpis: Dict[str, Any]) -> Dict[str, Any]:
    """Generates a unified risk score using operational, financial, and failure risk."""
    
    base_risk = failure_prediction.prediction_value * 100
    
    # Simple risk matrix logic for demonstration
    financial_exposure = financial_kpis.get("total_asset_value", 0) * 0.05
    
    risk_level = "Critical" if base_risk > 75 else "High" if base_risk > 50 else "Moderate" if base_risk > 25 else "Low"
    
    return {
        "overall_risk_score": round(base_risk, 1),
        "risk_level": risk_level,
        "financial_exposure_estimate": financial_exposure,
        "explainability": {
            "primary_driver": "ML Failure Prediction" if base_risk > 50 else "Financial Exposure",
            "model_confidence": failure_prediction.confidence_score,
            "key_features": failure_prediction.feature_importance
        }
    }
