from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class AegonException(Exception):
    """Base class for all custom AEGON exceptions."""
    def __init__(self, message: str, status_code: int = 400, error_code: str = "BAD_REQUEST"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)

class NotFoundException(AegonException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404, error_code="NOT_FOUND")

class UnauthorizedException(AegonException):
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message, status_code=401, error_code="UNAUTHORIZED")

class ForbiddenException(AegonException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status_code=403, error_code="FORBIDDEN")

class ValidationException(AegonException):
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=422, error_code="VALIDATION_ERROR")

class BusinessRuleException(AegonException):
    def __init__(self, message: str):
        super().__init__(message, status_code=409, error_code="BUSINESS_RULE_VIOLATION")

async def aegon_exception_handler(request: Request, exc: AegonException):
    logger.error(f"AegonException: {exc.error_code} - {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.error_code, "message": exc.message}},
    )

async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled server error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred."}},
    )
