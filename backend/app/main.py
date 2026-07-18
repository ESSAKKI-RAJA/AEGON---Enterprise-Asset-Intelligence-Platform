import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import setup_middlewares
from app.core.container import Container
from app.api.v1 import (
    auth, assets, maintenance, inventory, finance, procurement, analytics, ai, realtime, settings as settings_api, search, vision, health
)
from app.core.exceptions import AegonException, aegon_exception_handler, global_exception_handler
from app.core.database import init_db

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("STEP 1: Starting AEGON lifespan")
    setup_logging()
    print("STEP 2: Logging setup complete")
    
    # Initialize Database Lazily
    init_db()
    if not settings.DATABASE_URL:
        logger.warning("DATABASE_URL environment variable is missing. Operating in degraded mode.")
    elif not settings.DATABASE_URL.startswith("postgresql+asyncpg://"):
        logger.warning("DATABASE_URL must use the asyncpg driver (e.g., postgresql+asyncpg://...). Connection might fail.")
    
    print("STEP 3: Database configuration validated")
    
    container = Container()
    print("STEP 4: Container created")
    container.wire(packages=["app.api.v1"])
    print("STEP 5: Container wired")
    app.container = container # type: ignore
    
    print("STEP 6: Yielding to FastAPI")
    yield
    print("STEP 7: Lifespan shutdown")

app = FastAPI(
    title="AEGON Enterprise API",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

setup_middlewares(app)
app.add_exception_handler(AegonException, aegon_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Include AEGON Enterprise Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(assets.router, prefix=f"{settings.API_V1_STR}/assets", tags=["assets"])
app.include_router(maintenance.router, prefix=f"{settings.API_V1_STR}/maintenance", tags=["maintenance"])
app.include_router(inventory.router, prefix=f"{settings.API_V1_STR}/inventory", tags=["inventory"])
app.include_router(finance.router, prefix=f"{settings.API_V1_STR}/finance", tags=["finance"])
app.include_router(procurement.router, prefix=f"{settings.API_V1_STR}/procurement", tags=["procurement"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_STR}/analytics", tags=["analytics"])
app.include_router(ai.router, prefix=f"{settings.API_V1_STR}/ai", tags=["ai"])
app.include_router(realtime.router, prefix=f"{settings.API_V1_STR}/realtime", tags=["realtime"])
app.include_router(settings_api.router, prefix=f"{settings.API_V1_STR}/settings", tags=["settings"])
app.include_router(search.router, prefix=f"{settings.API_V1_STR}/search", tags=["search"])
app.include_router(vision.router, prefix=f"{settings.API_V1_STR}/vision", tags=["vision-intelligence"])
app.include_router(health.router, tags=["health"])
