from pydantic import BaseModel
from typing import List

class FinanceKPIDTO(BaseModel):
    label: str
    value: str
    delta: str
    deltaPositive: bool
    deltaTone: str = "positive"

class BudgetDepartmentDTO(BaseModel):
    id: str
    department_name: str
    allocated_budget: float
    spent_ytd: float
    variance: float
    status: str

class FinanceIntelligenceDTO(BaseModel):
    insight: str
    reasoning: str
    action: str
    confidence: float

class FinanceOverviewResponse(BaseModel):
    kpis: List[FinanceKPIDTO]
    department_budgets: List[BudgetDepartmentDTO]
    insights: List[FinanceIntelligenceDTO]
