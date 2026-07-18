from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")

class StandardResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Request processed successfully"
    data: Optional[T] = None
    meta: Optional[dict] = None # For pagination (page, size, total)


