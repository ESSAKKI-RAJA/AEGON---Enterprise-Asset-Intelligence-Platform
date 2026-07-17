import time
import uuid
from typing import Callable
from fastapi import Request, Response, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import logging
from app.core.config import settings

logger = logging.getLogger("api.middleware")

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Correlation ID from header or generate new
        request_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
        except Exception as exc:
            logger.error(
                "Unhandled exception",
                extra={
                    "request_id": request_id,
                    "url": str(request.url),
                    "method": request.method,
                },
                exc_info=exc
            )
            raise exc
            
        process_time = time.time() - start_time
        
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "process_time_ms": round(process_time * 1000, 2),
            }
        )
        
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; object-src 'none';"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

def setup_middlewares(app: FastAPI):
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Enable GZip compression for responses > 1000 bytes
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(RequestIDMiddleware)
    
    # We can add TrustedHostMiddleware in production
    # app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
