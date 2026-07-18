from pydantic import BaseModel
from typing import List

class ProcurementKPIDTO(BaseModel):
    label: str
    value: str
    delta: str
    deltaPositive: bool
    deltaTone: str = "positive"

class PurchaseOrderDTO(BaseModel):
    id: str
    po_number: str
    vendor_name: str
    amount: float
    status: str
    delivery_risk: str
    created_at: str

class ProcurementIntelligenceDTO(BaseModel):
    insight: str
    reasoning: str
    action: str
    confidence: float

class ProcurementOverviewResponse(BaseModel):
    kpis: List[ProcurementKPIDTO]
    active_purchase_orders: List[PurchaseOrderDTO]
    insights: List[ProcurementIntelligenceDTO]
