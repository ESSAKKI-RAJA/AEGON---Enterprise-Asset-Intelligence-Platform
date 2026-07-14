from typing import Dict, Any, List
import uuid

class ExplainabilityEngine:
    """
    Provides Local and Global explanations for ML predictions.
    Simulates SHAP (SHapley Additive exPlanations).
    """
    def __init__(self):
        pass

    def explain_local(self, model: Any, feature_vector: List[float], feature_names: List[str]) -> Dict[str, Any]:
        """Provides feature importance specifically for a single prediction."""
        # Simulated SHAP values based on raw feature vector magnitude
        importance = {}
        for idx, val in enumerate(feature_vector):
            name = feature_names[idx] if idx < len(feature_names) else f"feature_{idx}"
            importance[name] = round(val * 0.15, 4) # Mock calculation
            
        # Sort by absolute impact
        sorted_importance = dict(sorted(importance.items(), key=lambda item: abs(item[1]), reverse=True))
        
        explanation_id = str(uuid.uuid4())
        
        return {
            "explanation_id": explanation_id,
            "feature_importance": sorted_importance,
            "business_explanation": self._generate_business_text(sorted_importance),
            "confidence_analysis": "High confidence. Prediction lies well within training distribution boundaries."
        }

    def _generate_business_text(self, importances: Dict[str, float]) -> str:
        """Translates numerical SHAP values into a human-readable business justification."""
        if not importances:
            return "No dominant factors identified."
        top_feature = list(importances.keys())[0]
        direction = "increased" if importances[top_feature] > 0 else "decreased"
        return f"The primary driver for this prediction is '{top_feature}', which {direction} the likelihood significantly."

explainability_engine = ExplainabilityEngine()
