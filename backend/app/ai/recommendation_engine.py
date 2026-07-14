from typing import Dict, Any, List

class RecommendationEngine:
    """
    Generates intelligent recommendations prioritizing business impact and confidence.
    """
    
    @staticmethod
    def generate_recommendation(
        context_type: str, 
        prediction_dto: Any = None, 
        kpis: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Creates a standardized recommendation payload.
        """
        # Mocking logic for the architectural scaffolding
        if context_type == "asset_replacement":
            return {
                "priority": "HIGH",
                "confidence": prediction_dto.confidence_score if prediction_dto else 0.8,
                "business_impact": "Prevents estimated $50,000 downtime cost.",
                "supporting_evidence": "Asset has reached end of useful life and failure probability is > 80%.",
                "source_predictions": [prediction_dto.model_name] if prediction_dto else [],
                "source_kpis": ["maintenance_cost_ytd", "utilization_rate"],
                "suggested_actions": [
                    "Initiate procurement for replacement",
                    "Schedule controlled decommissioning"
                ]
            }
        
        return {
            "priority": "LOW",
            "confidence": 0.5,
            "business_impact": "Routine optimization.",
            "supporting_evidence": "General platform heuristics.",
            "source_predictions": [],
            "source_kpis": [],
            "suggested_actions": ["Review in next cycle"]
        }

def rank_recommendations(recs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(recs, key=lambda x: x.get("confidence", 0), reverse=True)
