import uuid
from typing import List, Dict, Any
from app.services.base import BaseService, track_metrics
from app.repositories.base import UnitOfWork
from app.core.events import EventDispatcher
from app.ai.llm_gateway import llm_gateway
from app.services.analytics_service import AnalyticsService

class RecommendationService(BaseService):
    """
    Provides prioritized AI-driven recommendations across all modules.
    """
    def __init__(self, uow: UnitOfWork, analytics_service: AnalyticsService, event_dispatcher: EventDispatcher = None):
        super().__init__(uow, event_dispatcher)
        self.analytics_service = analytics_service

    @track_metrics("generate_recommendations")
    async def get_module_recommendations(self, module: str) -> List[Dict[str, Any]]:
        """
        Generates actionable recommendations for a specific module by combining rules + AI.
        """
        async def _operation():
            # In a real scenario, this would query module-specific ML models or rules.
            # Here, we generate dynamic mock recommendations for the scope of execution.
            
            recommendations = []
            if module == "assets":
                # Mocked ML + Rules output
                recommendations.append({
                    "priority": "high",
                    "title": "Replace Asset HVA-09",
                    "description": "HVAC unit HVA-09 has a 92% failure probability in the next 14 days due to sustained temperature anomalies.",
                    "action_link": "/assets/hva-09",
                    "action_text": "Schedule Replacement"
                })
            elif module == "maintenance":
                recommendations.append({
                    "priority": "medium",
                    "title": "Batch Work Orders",
                    "description": "5 pending work orders in Zone A can be batched to save 12 hours of technician transit time.",
                    "action_link": "/maintenance?zone=A",
                    "action_text": "View Batchable Orders"
                })
            elif module == "inventory":
                recommendations.append({
                    "priority": "high",
                    "title": "Stockout Risk: Hydraulic Fluid",
                    "description": "Current stock is below optimal reorder point. Projected to run out in 3 days based on current usage trends.",
                    "action_link": "/inventory/reorder",
                    "action_text": "Create Purchase Order"
                })
            else:
                # Default cross-module recommendation
                recommendations.append({
                    "priority": "low",
                    "title": "Review Access Logs",
                    "description": "3 new roles were created this week. Please review permissions.",
                    "action_link": "/settings",
                    "action_text": "Review Roles"
                })
                
            return recommendations

        return await self.execute_in_transaction(_operation)
