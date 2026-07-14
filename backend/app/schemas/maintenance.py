from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MaintenanceKPIDTO(BaseModel):
    label: str
    value: str
    delta: str
    deltaPositive: bool
    deltaTone: str = "positive"

class WorkOrderDTO(BaseModel):
    id: str
    wo_number: str
    title: str
    priority: str
    status: str
    asset_name: str
    created_at: str
    assigned_tech: Optional[str] = None
    predicted_downtime_hours: float
    failure_risk_score: float

class MaintenanceIntelligenceDTO(BaseModel):
    insight: str
    reasoning: str
    action: str
    confidence: float

class MaintenanceOverviewResponse(BaseModel):
    kpis: List[MaintenanceKPIDTO]
    recent_work_orders: List[WorkOrderDTO]
    insights: List[MaintenanceIntelligenceDTO]
