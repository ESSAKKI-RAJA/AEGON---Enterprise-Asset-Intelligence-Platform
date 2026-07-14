from typing import Dict, Any, List
from app.ml.features.pipelines import FEATURE_NAMES

class ExplainabilityEngine:
    """
    SHAP-like Explainable Machine Learning framework.
    Provides local explanations for individual predictions.
    """
    
    def explain_prediction(self, model: Any, feature_vector: List[float]) -> Dict[str, float]:
        """
        Lightweight stand-in for SHAP local explanations.
        In a real environment, we would use shap.TreeExplainer(model).shap_values(feature_vector).
        Here we proxy it by multiplying the global feature importance by the scaled feature vector.
        """
        if not hasattr(model, 'feature_importances_'):
            return {}
            
        importances = model.feature_importances_
        
        # Extremely naive localized attribution (importance * value) to simulate SHAP
        local_attribution = [
            float(importances[i] * feature_vector[i]) 
            for i in range(len(importances))
        ]
        
        # Normalize to sum to 1 (or 100%)
        total = sum(abs(a) for a in local_attribution)
        if total == 0:
            return {name: 0.0 for name in FEATURE_NAMES}
            
        normalized = [round((a / total) * 100, 2) for a in local_attribution]
        
        return dict(sorted(
            zip(FEATURE_NAMES, normalized),
            key=lambda x: abs(x[1]), reverse=True
        ))
