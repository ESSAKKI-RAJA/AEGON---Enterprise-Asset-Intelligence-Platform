from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import pandas as pd
from typing import Dict, Any

from app.services.base import BaseService, track_metrics
from app.repositories.base import UnitOfWork
from app.core.events import EventDispatcher
from app.repositories.asset import AssetRepository
from app.ai.budget_intelligence import analyze_cost_trend

class AIService(BaseService):
    def __init__(self, uow: UnitOfWork, event_dispatcher: EventDispatcher = None):
        super().__init__(uow, event_dispatcher)

    @track_metrics("evaluate_asset")
    async def evaluate_asset(self, asset_id: uuid.UUID) -> Dict[str, Any]:
        """Core AI pipeline for a single asset."""
        async def _operation():
            repo = self.uow.get_repository(AssetRepository)
            asset = await repo.get_by_id(asset_id)
            
            if not asset:
                return {"error": "Asset not found"}

            from app.ml.feature_engineering.asset_failure import build_asset_failure_features
            session = self.uow.session
            df = await build_asset_failure_features(session, asset_id=asset.id)
            
            if df.empty:
                return {"error": "Failed to extract features for asset"}
            
            try:
                from app.ml.inference.decision_engine import DecisionEngine
                engine = DecisionEngine()
                decisions = engine.generate_asset_decisions(df, [])
                if decisions:
                    decision = decisions[0]
                    return {
                        "asset_id": str(asset_id),
                        "features_snapshot": asset_data[0],
                        "health": {"score": asset.health_score},
                        "maintenance_recommendation": {
                            "action": decision.recommended_action,
                            "reasoning": decision.business_justification
                        },
                        "replacement_plan": {"status": "Review recommended"},
                        "feature_importance": {"impact": decision.financial_impact}
                    }
            except Exception as e:
                pass

            return {
                "asset_id": str(asset_id),
                "error": "ML Models not initialized"
            }
        
        return await self.execute_in_transaction(_operation)

    @track_metrics("analyze_enterprise_costs")
    async def analyze_enterprise_costs(self, trend_data: list) -> str:
        """Generates AI narrative for dashboard."""
        return await analyze_cost_trend(trend_data)
