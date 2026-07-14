from typing import Dict, Any

def recommend_maintenance_window(failure_probability: float, features: Dict[str, Any]) -> Dict[str, Any]:
    factors = []
    
    if failure_probability > 0.8:
        window = "immediate"
        factors.append("High predicted failure probability within 30 days.")
    elif failure_probability > 0.5:
        window = "next_30_days"
        factors.append("Moderate predicted failure probability.")
    else:
        window = "routine"
        factors.append("Low failure probability. Standard schedule applies.")
        
    if features.get("maintenance_count", 0) > 5 and failure_probability > 0.6:
        factors.append("Frequent past maintenance suggests systemic issue; consider replacement instead.")
        
    return {
        "recommended_window": window,
        "urgency": "high" if window in ["immediate", "next_30_days"] else "low",
        "factors_considered": factors
    }
