from typing import Dict, Any

def interpret_health_score(score: float, features: Dict[str, Any], feature_importances: Dict[str, float]) -> Dict[str, Any]:
    """
    Evaluates ML predictions + Analytics into an enterprise health assessment.
    """
    if score >= 80:
        status = "excellent"
    elif score >= 60:
        status = "good"
    elif score >= 40:
        status = "fair"
    elif score >= 20:
        status = "poor"
    else:
        status = "critical"

    factors = []
    # Use SHAP feature importances to explain the score
    for feature_name, impact in feature_importances.items():
        if abs(impact) > 15.0:  # If a feature shifts the score by > 15%
            direction = "reducing" if impact < 0 else "improving"
            factors.append(f"{feature_name} is significantly {direction} the health score (Impact: {impact}%).")
            
    if not factors:
        factors.append("Health score is stable with no dominating negative factors.")

    return {
        "score": round(score, 1),
        "status": status,
        "primary_drivers": factors,
        "recommendation_trigger": status in ["poor", "critical"]
    }
