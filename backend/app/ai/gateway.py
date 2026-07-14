from typing import Dict, Any, List
from app.services.analytics_service import AnalyticsService
from app.ml.gateway import ml_gateway

# Note: In a real implementation, we would inject all specific intelligence modules.
# For architecture demonstration, the Gateway acts as a facade.

class EnterpriseAIEngine:
    """
    Orchestrates Intelligence.
    Never executes SQL or trains models directly.
    Consumes AnalyticsEngine and MLPlatform.
    """
    def __init__(self, analytics_service: AnalyticsService):
        self.analytics_service = analytics_service
        self.ml_gateway = ml_gateway

    async def get_health_intelligence(self, asset_id: str, features: Dict[str, Any]) -> Dict[str, Any]:
        """Combines ML prediction and business analytics for an asset's health."""
        # 1. Get ML Prediction DTO
        ml_pred = self.ml_gateway.predict("health", features)
        
        # 2. Extract context from analytics (e.g. maintenance trends)
        # In a full app: analytics = await self.analytics_service.operational.get_asset_stats(asset_id)
        
        # 3. Delegate to Health Intelligence module (mocked inline here, full module below)
        from app.ai.health_intelligence import interpret_health_score
        return interpret_health_score(ml_pred.prediction_value, features, ml_pred.feature_importance)
        
    async def get_budget_intelligence(self) -> str:
        """Analyzes budget trends and generates LLM insights."""
        from app.ai.budget_intelligence import analyze_cost_trend
        # 1. Get Analytics Data
        trend = await self.analytics_service.financial.maintenance_cost_trend(months=3)
        # 2. Delegate to LLM Orchestrator
        return await analyze_cost_trend(trend)

# Instantiated by Dependency Injection in Routers
