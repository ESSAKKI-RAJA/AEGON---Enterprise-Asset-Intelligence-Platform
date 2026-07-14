from typing import Optional
from pydantic import EmailStr, Field
from app.schemas.base import BaseSchema, AuditableSchema
from uuid import UUID

# User Schemas
class UserBase(BaseSchema):
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool = True
    role_id: Optional[UUID] = None
    department_id: Optional[UUID] = None

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserUpdate(BaseSchema):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)
    role_id: Optional[UUID] = None
    department_id: Optional[UUID] = None

class UserInDB(UserBase, AuditableSchema):
    hashed_password: str

class UserResponse(UserBase, AuditableSchema):
    pass

# Role Schemas
class RoleBase(BaseSchema):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None

class RoleResponse(RoleBase, AuditableSchema):
    pass
