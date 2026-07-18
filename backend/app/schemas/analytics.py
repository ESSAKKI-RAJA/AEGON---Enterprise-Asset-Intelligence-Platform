from pydantic import BaseModel
from typing import List, Dict, Any

class AnalyticsKPIDTO(BaseModel):
    label: str
    value: str
    delta: str
    deltaPositive: bool
    deltaTone: str = "positive"

class EnterpriseRiskDTO(BaseModel):
    level: str
    primary_driver: str
    impact_area: str

class ExecutiveInsightDTO(BaseModel):
    insight: str
    reasoning: str
    action: str
    confidence: float
    domain: str

class AnalyticsOverviewResponse(BaseModel):
    kpis: List[AnalyticsKPIDTO]
    enterprise_risk: EnterpriseRiskDTO
    insights: List[ExecutiveInsightDTO]
    metrics_history: List[Dict[str, Any]]
