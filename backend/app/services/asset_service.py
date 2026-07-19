from typing import Optional
from datetime import datetime, timedelta
import uuid
from typing import Dict, Any

from app.models.asset import Asset
from app.repositories.asset import AssetRepository
from app.repositories.base import UnitOfWork
from app.services.base import BaseService, track_metrics
from app.core.events import EventDispatcher, DomainEvent
from app.core.rules import BusinessRule, RuleContext, BusinessRuleEngine
from app.core.workflow import WorkflowOrchestrator, WorkflowStep, WorkflowContext
from fastapi import HTTPException

# --- Domain Events ---
class AssetCriticalEvent(DomainEvent):
    def __init__(self, asset_name: str, department: str, **kwargs):
        super().__init__(**kwargs)
        self.asset_name = asset_name
        self.department = department

# --- Business Rules ---
class EvaluateWarrantyRule(BusinessRule):
    def get_name(self) -> str: return "EvaluateWarranty"
    def get_description(self) -> str: return "Evaluates the warranty status of an asset based on expiry date."
    
    async def evaluate(self, context: RuleContext) -> bool:
        return hasattr(context, "asset") and isinstance(context.asset, Asset)
        
    async def execute(self, context: RuleContext) -> dict:
        asset = context.asset
        if not asset.warranty_expiry:
            return {"status": "no_warranty", "days_remaining": None}
            
        expiry = asset.warranty_expiry.replace(tzinfo=None) if asset.warranty_expiry.tzinfo else asset.warranty_expiry
        days_remaining = (expiry - datetime.utcnow()).days
        
        if days_remaining < 0:
            status = "expired"
        elif days_remaining < 60:
            status = "expiring_soon"
        else:
            status = "active"
        
        return {"status": status, "days_remaining": days_remaining}

class GenerateReplacementPlanRule(BusinessRule):
    def get_name(self) -> str: return "GenerateReplacementPlan"
    def get_description(self) -> str: return "Generates a replacement plan recommendation based on age and health."
    
    async def evaluate(self, context: RuleContext) -> bool:
        return hasattr(context, "asset") and isinstance(context.asset, Asset)
        
    async def execute(self, context: RuleContext) -> dict:
        asset = context.asset
        if not asset.purchase_date:
            return {"asset_id": str(asset.id), "error": "Asset has no purchase date to evaluate age"}
            
        purchase_datetime = datetime.combine(asset.purchase_date, datetime.min.time())
        age_years = (datetime.utcnow() - purchase_datetime).days / 365.0
        
        if age_years > 7 and asset.health_score < 40:
            recommendation = "replace_immediately"
            rationale = "Asset exceeds typical lifecycle and health is critical."
        elif age_years > 5 and asset.health_score < 60:
            recommendation = "plan_replacement_next_budget_cycle"
            rationale = "Asset approaching end of useful life with declining health."
        else:
            recommendation = "maintain"
            rationale = "Asset within normal lifecycle parameters."
            
        return {
            "asset_id": str(asset.id), "age_years": round(age_years, 1),
            "health_score": asset.health_score, "recommendation": recommendation,
            "rationale": rationale,
        }

# --- Domain Events ---
class AssetRegisteredEvent(DomainEvent):
    def __init__(self, asset_id: uuid.UUID, asset_name: str, **kwargs):
        super().__init__(**kwargs)
        self.asset_id = asset_id
        self.asset_name = asset_name

class AssetTransferredEvent(DomainEvent):
    def __init__(self, asset_id: uuid.UUID, from_dept: str, to_dept: str, **kwargs):
        super().__init__(**kwargs)
        self.asset_id = asset_id
        self.from_dept = from_dept
        self.to_dept = to_dept

class AssetRetiredEvent(DomainEvent):
    def __init__(self, asset_id: uuid.UUID, reason: str, **kwargs):
        super().__init__(**kwargs)
        self.asset_id = asset_id
        self.reason = reason

# --- Workflow Steps ---
class RegisterAssetPersistenceStep(WorkflowStep):
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        
    def get_name(self) -> str: return "RegisterAssetPersistence"
    
    async def execute(self, context: WorkflowContext) -> None:
        data = context.get("data")
        actor = context.get("actor")
        
        asset = Asset(
            name=data["name"],
            barcode=data.get("barcode") or str(uuid.uuid4())[:8],
            category_id=uuid.UUID(data["category_id"]),
            subcategory_id=uuid.UUID(data["subcategory_id"]),
            department_id=uuid.UUID(data["department_id"]) if data.get("department_id") else None,
            purchase_date=data.get("purchase_date"),
            purchase_cost=data.get("purchase_cost"),
            current_value=data.get("purchase_cost"),
            warranty_expiry=data.get("warranty_expiry"),
            health_score=100.0,
            health_status="excellent",
            next_maintenance=datetime.utcnow() + timedelta(days=180),
        )
        repo = self.uow.get_repository(AssetRepository)
        asset = await repo.create(asset, audit_user=actor)
        context.set("asset", asset)
        
    async def compensate(self, context: WorkflowContext) -> None:
        asset = context.get("asset")
        if asset and asset.id:
            repo = self.uow.get_repository(AssetRepository)
            await repo.delete(asset.id, audit_user="system_rollback")

# --- Service ---
class AssetService(BaseService):
    def __init__(self, uow: UnitOfWork, event_dispatcher: Optional[EventDispatcher] = None):
        super().__init__(uow, event_dispatcher)
        self.rule_engine = BusinessRuleEngine()

    @track_metrics("register_asset")
    async def register_asset(self, data: dict, actor: str = "system") -> Asset:
        """Full registration workflow orchestrating multiple steps."""
        context = WorkflowContext(data=data, actor=actor)
        orchestrator = WorkflowOrchestrator("Register Asset Workflow")
        
        orchestrator.add_step(RegisterAssetPersistenceStep(self.uow))
        
        async def _operation():
            await orchestrator.execute(context)
            return context.get("asset")
            
        asset = await self.execute_in_transaction(_operation)
        await self.publish_event(AssetRegisteredEvent(asset.id, asset.name))
        return asset

    @track_metrics("search_assets")
    async def search_assets(self, query: str, page: int = 1, page_size: int = 20) -> dict:
        """Enterprise search for assets."""
        async def _operation():
            repo = self.uow.get_repository(AssetRepository)
            return await repo.search_assets(query=query, page=page, page_size=page_size)
        
        result = await self.execute_in_transaction(_operation)
        return {
            "items": result.items,
            "total": result.total,
            "page": result.page,
            "page_size": result.page_size
        }

    @track_metrics("get_asset_digital_twin")
    async def get_asset_digital_twin(self, asset_id: uuid.UUID) -> dict:
        """Constructs the comprehensive Enterprise Digital Twin for an asset."""
        from app.analytics.asset_intelligence import AssetIntelligenceEngine
        
        async def _operation():
            repo = self.uow.get_repository(AssetRepository)
            asset = await repo.get_by_id(asset_id)
            if not asset:
                raise HTTPException(status_code=404, detail="Asset not found")
                
            intelligence = AssetIntelligenceEngine(asset, self.uow)
            digital_twin_data = await intelligence.generate_digital_twin()
            
            # Combine the ORM model data with the intelligence data
            result = {
                "identity": {
                    "id": str(asset.id),
                    "name": asset.name,
                    "barcode": asset.barcode,
                    "serial_number": asset.serial_number,
                    "model_number": asset.model_number,
                    "status": asset.status.value if hasattr(asset.status, 'value') else asset.status,
                    "category": asset.category.name if asset.category else "Uncategorized",
                    "department": asset.department.name if asset.department else "Unassigned"
                },
                "lifecycle": {
                    "purchase_date": asset.purchase_date.isoformat() if asset.purchase_date else None,
                    "warranty_expiry": asset.warranty_expiry.isoformat() if asset.warranty_expiry else None,
                    "last_maintenance": asset.last_maintenance.isoformat() if asset.last_maintenance else None,
                    "next_maintenance": asset.next_maintenance.isoformat() if asset.next_maintenance else None,
                },
                "intelligence": digital_twin_data,
                "relationships": {
                    "work_orders": len(asset.work_orders) if hasattr(asset, 'work_orders') else 0,
                    "documents": len(asset.documents) if hasattr(asset, 'documents') else 0
                }
            }
            return result
            
        return await self.execute_in_transaction(_operation)

    @track_metrics("transfer_asset")
    async def transfer_asset(self, asset_id: uuid.UUID, new_department_id: uuid.UUID, actor: str = "system") -> Asset:
        async def _operation():
            repo = self.uow.get_repository(AssetRepository)
            asset = await repo.get_by_id_or_raise(asset_id)
            old_department = str(asset.department_id) if asset.department_id else "None"
            
            asset.department_id = new_department_id
            asset.utilization_rate = 0.0  # reset — new department starts fresh
            
            await repo.update(asset, audit_user=actor)
            return asset, old_department
            
        asset, old_department = await self.execute_in_transaction(_operation)
        await self.publish_event(AssetTransferredEvent(asset.id, old_department, str(new_department_id)))
        return asset

    @track_metrics("retire_asset")
    async def retire_asset(self, asset_id: uuid.UUID, reason: str, actor: str = "system") -> Asset:
        async def _operation():
            repo = self.uow.get_repository(AssetRepository)
            asset = await repo.get_by_id_or_raise(asset_id)
            asset.health_status = "retired"
            await repo.update(asset, audit_user=actor)
            return asset
            
        asset = await self.execute_in_transaction(_operation)
        await self.publish_event(AssetRetiredEvent(asset.id, reason))
        return asset

    @track_metrics("evaluate_warranty")
    async def evaluate_warranty(self, asset_id: uuid.UUID) -> dict:
        repo = self.uow.get_repository(AssetRepository)
        asset = await repo.get_by_id_or_raise(asset_id)
        
        context = RuleContext(asset=asset)
        return await self.rule_engine.run(EvaluateWarrantyRule(), context)

    @track_metrics("generate_replacement_plan")
    async def generate_replacement_plan(self, asset_id: uuid.UUID) -> dict:
        repo = self.uow.get_repository(AssetRepository)
        asset = await repo.get_by_id_or_raise(asset_id)
        
        context = RuleContext(asset=asset)
        return await self.rule_engine.run(GenerateReplacementPlanRule(), context)

    @track_metrics("update_health")
    async def update_health(self, asset_id: uuid.UUID, score: float, status: str):
        async def _operation():
            repo = self.uow.get_repository(AssetRepository)
            asset = await repo.get_by_id_or_raise(asset_id)
            asset.health_score = score
            asset.health_status = status
            await repo.update(asset, audit_user="system")
            return asset
            
        asset = await self.execute_in_transaction(_operation)
        
        if status == "critical":
            department = str(asset.department_id) if asset.department_id else "Unknown"
            await self.publish_event(AssetCriticalEvent(asset.name, department))
            
        return asset

    # --- Aggregation Methods for Analytics Engine ---
    @track_metrics("get_asset_summary_stats")
    async def get_asset_summary_stats(self) -> Dict[str, Any]:
        """Provides aggregated asset stats for the Analytics Engine."""
        async def _operation():
            repo = self.uow.get_repository(AssetRepository)
            return await repo.get_summary_stats()
        return await self.execute_in_transaction(_operation)

    @track_metrics("get_department_rankings")
    async def get_department_rankings(self) -> list:
        async def _operation():
            repo = self.uow.get_repository(AssetRepository)
            return await repo.get_department_rankings()
        return await self.execute_in_transaction(_operation)
