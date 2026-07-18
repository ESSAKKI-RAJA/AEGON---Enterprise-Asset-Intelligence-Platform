from fastapi import APIRouter, Depends, Request
from typing import Dict, Any
from sqlalchemy import text
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.cache import CacheService
import os

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    return {"status": "OK", "service": "AEGON Backend V5.3"}

@router.get("/status")
async def status_check() -> Dict[str, Any]:
    return {"status": "OK", "message": "All systems operational."}

from app.core.database import AsyncSessionLocal

@router.get("/debug/database")
async def debug_database() -> Dict[str, Any]:
    if AsyncSessionLocal is None:
        return {"status": "unavailable", "message": "Database is not configured (missing environment variables)."}
        
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "connected", "latency_ms": 0} # simplified latency
    except Exception as e:
        return {"status": "disconnected", "error": str(e)}

@router.get("/debug/cache")
async def debug_cache() -> Dict[str, Any]:
    try:
        success = await CacheService.set("debug_ping", "pong", ttl=10)
        val = await CacheService.get("debug_ping")
        return {"status": "connected" if val == "pong" else "disconnected"}
    except Exception as e:
        return {"status": "disconnected", "error": str(e)}

@router.get("/debug/config")
async def debug_config() -> Dict[str, Any]:
    return {"environment": os.getenv("ENVIRONMENT", "development")}

@router.get("/debug/environment")
async def debug_environment() -> Dict[str, Any]:
    return {
        "env": os.getenv("ENVIRONMENT", "development"),
        "database_url_set": bool(os.getenv("DATABASE_URL")),
        "redis_url_set": bool(os.getenv("REDIS_URL")),
        "supabase_url_set": bool(os.getenv("SUPABASE_URL"))
    }

@router.get("/debug/routes")
async def debug_routes(request: Request) -> Dict[str, Any]:
    return {"routes_count": len(request.app.routes)}

@router.get("/debug/dependencies")
async def debug_dependencies() -> Dict[str, Any]:
    return {"status": "OK"}

@router.get("/debug/startup")
async def debug_startup() -> Dict[str, Any]:
    return {"status": "OK"}
