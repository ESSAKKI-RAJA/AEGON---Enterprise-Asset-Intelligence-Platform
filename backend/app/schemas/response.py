from typing import Generic, TypeVar, Optional, Any, List
from pydantic import BaseModel

T = TypeVar("T")

class StandardResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Request processed successfully"
    data: Optional[T] = None
    meta: Optional[dict] = None # For pagination (page, size, total)

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: str
    details: Optional[Any] = None

class PaginatedParams(BaseModel):
    skip: int = 0
    limit: int = 20
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "asc"
