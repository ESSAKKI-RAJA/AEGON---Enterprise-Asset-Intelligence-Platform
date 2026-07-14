from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional, Any, Dict

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class AuditableSchema(BaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    is_deleted: bool = False
    metadata_: Optional[Dict[str, Any]] = None
