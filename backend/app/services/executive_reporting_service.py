import io
from typing import Dict, Any
from app.services.base import BaseService, track_metrics
from app.repositories.base import UnitOfWork
from app.core.events import EventDispatcher
from app.services.analytics_service import AnalyticsService
from app.ai.llm_gateway import llm_gateway
import datetime

class ExecutiveReportingService(BaseService):
    """
    Generates dynamic executive reports combining raw Python data analytics and LLM summaries.
    """
    def __init__(self, uow: UnitOfWork, analytics_service: AnalyticsService, event_dispatcher: EventDispatcher = None):
        super().__init__(uow, event_dispatcher)
        self.analytics_service = analytics_service

    @track_metrics("generate_executive_report")
    async def generate_report(self) -> Dict[str, Any]:
        """Generates a structured executive report."""
        async def _operation():
            # 1. Fetch Analytics Data
            # For demonstration, we use static data structure similar to executive dashboard
            raw_data = {
                "total_assets": 1205,
                "critical_health": 45,
                "maintenance_cost_ytd": 1250000,
                "roi_improvement": "+14%"
            }
            
            # 2. Get AI Summary
            context = (
                f"Total Assets: {raw_data['total_assets']}, "
                f"Assets in Critical Health: {raw_data['critical_health']}, "
                f"Maintenance Cost YTD: ${raw_data['maintenance_cost_ytd']}, "
                f"ROI Improvement: {raw_data['roi_improvement']}."
            )
            
            ai_summary = await llm_gateway.generate_explanation(
                context=context,
                prompt="Summarize the enterprise asset health and financial performance for the executive board."
            )

            # 3. Compile Report
            report = {
                "report_id": f"EXEC-{datetime.datetime.utcnow().strftime('%Y%m%d')}",
                "generated_at": datetime.datetime.utcnow().isoformat(),
                "data_snapshot": raw_data,
                "executive_summary": ai_summary.get("Reason", "No summary available."),
                "strategic_recommendation": ai_summary.get("RecommendedAction", "Continue monitoring.")
            }
            
            return report

        return await self.execute_in_transaction(_operation)
