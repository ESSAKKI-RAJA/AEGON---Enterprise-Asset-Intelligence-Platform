from typing import Any, Dict, Optional
from app.repositories.base import RepositoryException, EntityNotFound, EntityAlreadyExists

class EnterpriseServiceException(Exception):
    """Base exception for all business service layer errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}
        self.message = message

class ValidationException(EnterpriseServiceException):
    """Raised when request or business rule validation fails."""
    pass

class BusinessRuleException(EnterpriseServiceException):
    """Raised when a specific business rule is violated."""
    pass

class WorkflowException(EnterpriseServiceException):
    """Raised when a workflow orchestration fails."""
    pass

class ServiceEntityNotFound(EnterpriseServiceException):
    """Raised when an entity requested by the service is not found."""
    pass

class ServiceEntityAlreadyExists(EnterpriseServiceException):
    """Raised when attempting to create an entity that already exists."""
    pass

def translate_repo_exception(exc: Exception) -> Exception:
    """
    Translates Repository exceptions into Enterprise Service exceptions
    so that higher layers (like Routers) never deal with Repo/DB exceptions.
    """
    if isinstance(exc, EntityNotFound):
        return ServiceEntityNotFound(str(exc))
    if isinstance(exc, EntityAlreadyExists):
        return ServiceEntityAlreadyExists(str(exc))
    if isinstance(exc, RepositoryException):
        # Fallback for other repo errors
        return EnterpriseServiceException(f"Repository operation failed: {str(exc)}")
    
    # If it's already a service exception or an unknown system exception, return as is.
    # In practice, unhandled DB errors would be caught by repo layer and wrapped in RepositoryException.
    return exc
