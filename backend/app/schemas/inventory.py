from pydantic import BaseModel
from typing import List, Optional

class InventoryKPIDTO(BaseModel):
    label: str
    value: str
    delta: str
    deltaPositive: bool
    deltaTone: str = "positive"

class InventoryItemDTO(BaseModel):
    id: str
    part_number: str
    name: str
    category: str
    current_stock: int
    unit: str
    unit_cost: float
    reorder_point: float
    stock_risk: str
    eoq: int

class InventoryIntelligenceDTO(BaseModel):
    insight: str
    reasoning: str
    action: str
    confidence: float

class InventoryOverviewResponse(BaseModel):
    kpis: List[InventoryKPIDTO]
    low_stock_items: List[InventoryItemDTO]
    insights: List[InventoryIntelligenceDTO]
