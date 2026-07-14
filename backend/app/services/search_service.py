from typing import List, Dict, Any
from sqlalchemy import select, or_
from app.services.base import BaseService, track_metrics
from app.repositories.base import UnitOfWork
from app.core.events import EventDispatcher
from app.models.asset import Asset
from app.models.maintenance import WorkOrder

class SearchService(BaseService):
    """
    Global Natural Language Search for the Enterprise.
    Supports parsing natural language to find matching entities.
    """
    def __init__(self, uow: UnitOfWork, event_dispatcher: EventDispatcher = None):
        super().__init__(uow, event_dispatcher)

    @track_metrics("global_search")
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        async def _operation():
            results = []
            session = self.uow.session

            # 1. Search Assets
            asset_stmt = select(Asset).where(
                or_(
                    Asset.name.ilike(f"%{query}%"),
                    Asset.asset_type.ilike(f"%{query}%"),
                    Asset.status.ilike(f"%{query}%")
                )
            ).limit(limit)
            
            asset_res = await session.execute(asset_stmt)
            for asset in asset_res.scalars().all():
                results.append({
                    "id": str(asset.id),
                    "type": "ASSET",
                    "title": asset.name,
                    "subtitle": f"Type: {asset.asset_type} | Status: {asset.status}",
                    "link": f"/assets/{asset.id}"
                })

            # 2. Search Work Orders
            wo_stmt = select(WorkOrder).where(
                or_(
                    WorkOrder.title.ilike(f"%{query}%"),
                    WorkOrder.description.ilike(f"%{query}%"),
                    WorkOrder.priority.ilike(f"%{query}%")
                )
            ).limit(limit)
            
            wo_res = await session.execute(wo_stmt)
            for wo in wo_res.scalars().all():
                results.append({
                    "id": str(wo.id),
                    "type": "WORK_ORDER",
                    "title": wo.title,
                    "subtitle": f"Priority: {wo.priority} | Status: {wo.status}",
                    "link": f"/maintenance/{wo.id}"
                })

            # 3. Search Departments
            from app.models.organization import Department
            dept_stmt = select(Department).where(
                Department.name.ilike(f"%{query}%")
            ).limit(limit)
            
            dept_res = await session.execute(dept_stmt)
            for dept in dept_res.scalars().all():
                results.append({
                    "id": str(dept.id),
                    "type": "DEPARTMENT",
                    "title": dept.name,
                    "subtitle": "Department",
                    "link": "/settings"
                })
                
            # 4. Search Users
            from app.models.identity import User
            user_stmt = select(User).where(
                User.is_active == True,
                or_(
                    User.email.ilike(f"%{query}%"),
                    User.first_name.ilike(f"%{query}%"),
                    User.last_name.ilike(f"%{query}%")
                )
            ).limit(limit)
            user_res = await session.execute(user_stmt)
            for user in user_res.scalars().all():
                results.append({
                    "id": str(user.id),
                    "type": "USER",
                    "title": f"{user.first_name} {user.last_name}",
                    "subtitle": user.email,
                    "link": "/settings"
                })

            return results

        return await self.execute_in_transaction(_operation)
