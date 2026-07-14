from typing import Optional, List, Any
from pydantic import Field, AliasChoices, model_validator, BaseModel
from app.schemas.base import BaseSchema, AuditableSchema
from uuid import UUID
from datetime import date
from app.models.asset import AssetStatus

# Asset Schemas
class AssetBase(BaseSchema):
    name: str
    tag_number: str
    serial_number: Optional[str] = None
    status: AssetStatus = AssetStatus.ACTIVE
    purchase_date: Optional[date] = None
    purchase_price: Optional[float] = None
    category_id: UUID
    room_id: Optional[UUID] = None
    vendor_id: Optional[UUID] = None
    department_id: Optional[UUID] = None

class AssetCreate(AssetBase):
    pass

class AssetUpdate(BaseSchema):
    name: Optional[str] = None
    tag_number: Optional[str] = None
    serial_number: Optional[str] = None
    status: Optional[AssetStatus] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[float] = None
    category_id: Optional[UUID] = None
    room_id: Optional[UUID] = None
    vendor_id: Optional[UUID] = None
    department_id: Optional[UUID] = None

class AssetResponse(AuditableSchema):
    name: str
    code: str = Field(validation_alias=AliasChoices('code', 'barcode', 'tag_number'))
    serial_number: Optional[str] = None
    status: AssetStatus = AssetStatus.ACTIVE
    purchase_date: Optional[date] = None
    purchaseValue: Optional[float] = Field(None, validation_alias=AliasChoices('purchaseValue', 'purchase_cost', 'purchase_price'))
    health: float = Field(100.0, validation_alias=AliasChoices('health', 'health_score'))
    category: Optional[str] = None
    department: Optional[str] = None
    room_id: Optional[UUID] = None
    vendor_id: Optional[UUID] = None
    
    @model_validator(mode='before')
    @classmethod
    def resolve_relationships(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if data.get('category') and hasattr(data['category'], 'name'):
                data['category'] = data['category'].name
            if data.get('department') and hasattr(data['department'], 'name'):
                data['department'] = data['department'].name
            return data
            
        res = {
            "name": getattr(data, 'name', None),
            "code": getattr(data, 'barcode', getattr(data, 'tag_number', '')),
            "serial_number": getattr(data, 'serial_number', None),
            "status": getattr(data, 'status', AssetStatus.ACTIVE),
            "purchase_date": getattr(data, 'purchase_date', None),
            "purchaseValue": getattr(data, 'purchase_cost', getattr(data, 'purchase_price', None)),
            "health": getattr(data, 'health_score', 100.0),
            "category": data.category.name if getattr(data, 'category', None) else None,
            "department": data.department.name if getattr(data, 'department', None) else None,
            "room_id": getattr(data, 'room_id', None),
            "vendor_id": getattr(data, 'vendor_id', None),
            "id": getattr(data, 'id', None),
            "created_at": getattr(data, 'created_at', None),
            "updated_at": getattr(data, 'updated_at', None),
            "created_by": getattr(data, 'created_by', None),
            "updated_by": getattr(data, 'updated_by', None),
        }
        return res

class AssetIdentityDTO(BaseModel):
    id: str
    name: str
    barcode: str
    serial_number: Optional[str] = None
    model_number: Optional[str] = None
    status: str
    category: str
    department: str

class AssetLifecycleDTO(BaseModel):
    purchase_date: Optional[str] = None
    warranty_expiry: Optional[str] = None
    last_maintenance: Optional[str] = None
    next_maintenance: Optional[str] = None

class AssetHealthIntelligenceDTO(BaseModel):
    score: float
    status: str
    age_years: float
    utilization_rate: float

class AssetRiskIntelligenceDTO(BaseModel):
    failure_probability: str
    confidence: str
    business_impact: str
    reason: str
    data_used: str
    recommended_action: str
    estimated_remaining_useful_life: str
    estimated_repair_cost: str

class AssetFinancialIntelligenceDTO(BaseModel):
    purchase_cost: float
    current_value: float
    accumulated_depreciation: float
    maintenance_cost_ytd: float
    lifecycle_cost: float
    roi: str

class AssetIntelligenceDTO(BaseModel):
    health_intelligence: AssetHealthIntelligenceDTO
    risk_intelligence: AssetRiskIntelligenceDTO
    financial_intelligence: AssetFinancialIntelligenceDTO

class AssetRelationshipsDTO(BaseModel):
    work_orders: int
    documents: int

class AssetDigitalTwinResponse(BaseModel):
    identity: AssetIdentityDTO
    lifecycle: AssetLifecycleDTO
    intelligence: AssetIntelligenceDTO
    relationships: AssetRelationshipsDTO

class AssetRegistryResponse(BaseModel):
    items: List[AssetResponse]
    total: int
    page: int
    page_size: int

