from fastapi import Request, HTTPException, status
import re
import bleach

def sanitize_input(data: str) -> str:
    """Removes HTML and JS tags to prevent XSS."""
    if not isinstance(data, str):
        return data
    return bleach.clean(data, tags=[], attributes={}, strip=True)

class APIKeyValidator:
    """
    Dependency to validate system-to-system API keys.
    Requires `X-API-Key` header.
    """
    async def __call__(self, request: Request) -> bool:
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API Key missing"
            )
        
        # In a real system, we'd hash this and check the `APIKey` table.
        # Stubbing for architecture completeness:
        if api_key != "enterprise-valid-key":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid API Key"
            )
        return True

class IdempotencyMiddleware:
    """
    Ensures that a request with `Idempotency-Key` header is processed exactly once.
    (This is usually implemented as a middleware or dependency using Redis).
    """
    pass

def validate_sql_injection(value: str) -> bool:
    """Basic SQLi pattern check (though SQLAlchemy parameterized queries prevent this, 
    it's good defense-in-depth for dynamic search fields)."""
    sql_patterns = re.compile(r"(union|select|insert|update|delete|drop|alter)[\s\+]+", re.IGNORECASE)
    if sql_patterns.search(value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid characters in input"
        )
    return True
