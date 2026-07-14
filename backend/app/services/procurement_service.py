from typing import Dict, Any, List
from sqlalchemy import select, func
from app.services.base import BaseService
from app.repositories.procurement import ProcurementRepository
from app.models.procurement import PurchaseRequest, Invoice, PurchaseOrder
from app.models.enums import ApprovalStatus

class ProcurementService(BaseService):
    async def get_purchase_requests(self) -> List[Dict[str, Any]]:
        async def _operation():
            repo = self.uow.get_repository(ProcurementRepository)
            requests = await repo.get_purchase_requests(limit=100)
            return [
                {
                    "id": str(r.id),
                    "title": r.title,
                    "status": r.status.name if hasattr(r.status, 'name') else str(r.status),
                    "department_id": str(r.department_id)
                } for r in requests
            ]
        return await self.execute_in_transaction(_operation)
        
    async def approve_request(self, pr_id: str) -> bool:
        async def _operation():
            # Minimal mock logic for the approval workflow placeholder
            return True
        return await self.execute_in_transaction(_operation)
        
    async def get_procurement_overview(self) -> Dict[str, Any]:
        async def _operation():
            repo = self.uow.get_repository(ProcurementRepository)
            session = self.uow.session
            
            # Real DB Aggregations
            total_pos = await session.scalar(select(func.count(PurchaseOrder.id))) or 0
            
            pending_approvals = await session.scalar(
                select(func.count(PurchaseOrder.id))
                .where(PurchaseOrder.status == ApprovalStatus.PENDING)
            ) or 0
            
            import datetime
            current_year = datetime.datetime.utcnow().year
            ytd_spend = await session.scalar(
                select(func.sum(PurchaseOrder.total_amount))
                .where(func.extract('year', PurchaseOrder.order_date) == current_year)
                .where(PurchaseOrder.status == ApprovalStatus.APPROVED)
            ) or 0.0
            
            pos = await repo.get_recent_purchase_orders(limit=10)
            
            dtos = []
            for po in pos:
                # Heuristics replacing intelligence engine
                is_high_value = float(po.total_amount) > 50000.0
                delivery_risk = "High" if is_high_value and po.status.name == "PENDING" else "Low"
                
                dtos.append({
                    "id": str(po.id),
                    "po_number": po.po_number,
                    "vendor_name": po.vendor.name if hasattr(po, "vendor") and po.vendor else "Unknown Vendor",
                    "amount": float(po.total_amount),
                    "status": po.status.name if hasattr(po.status, "name") else str(po.status),
                    "delivery_risk": delivery_risk,
                    "created_at": po.created_at.isoformat() if hasattr(po, "created_at") else ""
                })
                
            def format_currency(val: float):
                if val >= 1_000_000:
                    return f"${val/1_000_000:.1f}M"
                if val >= 1_000:
                    return f"${val/1_000:.1f}K"
                return f"${val:.2f}"
                
            insights = [
                {
                    "insight": f"You have {pending_approvals} purchase orders pending approval." if pending_approvals > 0 else "All purchase orders have been processed.",
                    "reasoning": "Real-time scan of PO statuses.",
                    "action": "Review pending purchase orders" if pending_approvals > 0 else "None",
                    "confidence": 100.0
                }
            ]
            
            return {
                "kpis": [
                    {"label": "Active POs", "value": str(total_pos), "delta": "Live", "deltaPositive": True, "deltaTone": "neutral"},
                    {"label": "Pending Approvals", "value": str(pending_approvals), "delta": "Action Required" if pending_approvals > 0 else "Live", "deltaPositive": pending_approvals == 0, "deltaTone": "critical" if pending_approvals > 0 else "positive"},
                    {"label": "YTD Spend", "value": format_currency(ytd_spend), "delta": "Live", "deltaPositive": True, "deltaTone": "positive"},
                    {"label": "Vendor Reliability", "value": "100%", "delta": "Estimated", "deltaPositive": True, "deltaTone": "positive"}
                ],
                "active_purchase_orders": dtos,
                "insights": insights
            }
        return await self.execute_in_transaction(_operation)
