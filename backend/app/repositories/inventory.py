from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository, translate_db_exception, CacheHook, AuditHook
from app.models.inventory import InventoryItem


class InventoryRepository(BaseRepository[InventoryItem]):
    """Inventory domain repository specializing in spare parts and stock levels."""
    
    def __init__(
        self,
        session: AsyncSession,
        cache_hook: Optional[CacheHook] = None,
        audit_hook: Optional[AuditHook] = None,
    ):
        super().__init__(
            session=session,
            model_class=InventoryItem,
            cache_hook=cache_hook,
            audit_hook=audit_hook,
        )

    async def get_by_sku(self, sku: str) -> Optional[InventoryItem]:
        """Retrieve an inventory item by its unique SKU code."""
        try:
            stmt = select(self.model_class).where(
                self.model_class.sku == sku,
                self.model_class.is_deleted .is_(False)
            )
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            raise translate_db_exception(e)

    async def find_low_stock(
        self,
        warehouse_id: Optional[UUID] = None
    ) -> List[InventoryItem]:
        """Find items where quantity is below or equal to the reorder level."""
        try:
            stmt = select(self.model_class).where(
                self.model_class.quantity <= self.model_class.reorder_level,
                self.model_class.is_deleted .is_(False)
            )
            if warehouse_id:
                stmt = stmt.where(self.model_class.warehouse_id == warehouse_id)
                
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise translate_db_exception(e)

    async def calculate_abc_analysis(
        self,
        warehouse_id: Optional[UUID] = None
    ) -> dict:
        """
        ABC analysis (Pareto) for inventory items based on their total value (quantity * unit_price).
        Returns classification segments A (top 80% value), B (next 15%), and C (remaining 5%).
        """
        try:
            stmt = select(self.model_class).where(self.model_class.is_deleted .is_(False))
            if warehouse_id:
                stmt = stmt.where(self.model_class.warehouse_id == warehouse_id)
                
            result = await self.session.execute(stmt)
            items = list(result.scalars().all())
            
            if not items:
                return {"A": [], "B": [], "C": []}
            
            # Sort items by their total valuation desc
            items_sorted = sorted(
                items,
                key=lambda x: (x.quantity * x.unit_price),
                reverse=True
            )
            
            total_valuation = sum(x.quantity * x.unit_price for x in items_sorted)
            if total_valuation == 0:
                # Fallback: simple split if all values are zero
                split_idx_a = int(len(items_sorted) * 0.2)
                split_idx_b = int(len(items_sorted) * 0.5)
                return {
                    "A": items_sorted[:split_idx_a],
                    "B": items_sorted[split_idx_a:split_idx_b],
                    "C": items_sorted[split_idx_b:]
                }
            
            a_items = []
            b_items = []
            c_items = []
            
            cumulative_val = 0.0
            for item in items_sorted:
                item_val = item.quantity * item.unit_price
                cumulative_val += item_val
                percentage = (cumulative_val / total_valuation) * 100.0
                
                if percentage <= 80.0:
                    a_items.append(item)
                elif percentage <= 95.0:
                    b_items.append(item)
                else:
                    c_items.append(item)
                    
            return {
                "A": a_items,
                "B": b_items,
                "C": c_items
            }
        except Exception as e:
            raise translate_db_exception(e)

    async def count_items(self) -> int:
        from sqlalchemy import select, func
        try:
            stmt = select(func.count(self.model_class.id)).where(
                self.model_class.is_deleted .is_(False)
            )
            res = await self.session.execute(stmt)
            return res.scalar() or 0
        except Exception as e:
            raise translate_db_exception(e)
