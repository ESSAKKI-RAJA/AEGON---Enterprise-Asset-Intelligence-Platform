"""
AEGON API Dependencies — Enterprise Evaluation Edition
========================================================
Provides FastAPI dependency injection for database sessions and services.

Authentication is bypassed in this evaluation edition. All auth-gated
dependencies return the static Enterprise Evaluation User.

In production, `get_current_user` verifies a Supabase RS256 JWT against
SUPABASE_JWKS_URL, looks up the user in PostgreSQL, and enforces RBAC/ABAC.
"""

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.events import dispatcher
from app.core.demo_user import DEMO_USER, DemoUser
from app.repositories.base import UnitOfWork
from app.services.user_service import UserService
from app.services.asset_service import AssetService
from app.services.maintenance_service import MaintenanceService
from app.services.inventory_service import InventoryService
from app.services.procurement_service import ProcurementService
from app.services.finance_service import FinanceService
from app.services.analytics_service import AnalyticsService
from app.services.auth_service import AuthService

import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


def get_uow(db: AsyncSession = Depends(get_db)) -> UnitOfWork:
    return UnitOfWork(db)


# ---------------------------------------------------------------------------
# Demo Authentication — Enterprise Evaluation Mode
# ---------------------------------------------------------------------------

def get_current_user() -> DemoUser:
    """
    Returns the static Enterprise Evaluation User.
    In production this verifies a Supabase JWT and looks up the DB record.
    """
    return DEMO_USER


def get_current_active_superuser() -> DemoUser:
    """Always grants super-admin access in evaluation mode."""
    return DEMO_USER


# ---------------------------------------------------------------------------
# Service factories
# ---------------------------------------------------------------------------

def get_user_service(uow: UnitOfWork = Depends(get_uow)) -> UserService:
    return UserService(uow=uow, event_dispatcher=dispatcher)


def get_auth_service(uow: UnitOfWork = Depends(get_uow)) -> AuthService:
    return AuthService(uow=uow, event_dispatcher=dispatcher)


def get_asset_service(uow: UnitOfWork = Depends(get_uow)) -> AssetService:
    return AssetService(uow=uow, event_dispatcher=dispatcher)


def get_maintenance_service(uow: UnitOfWork = Depends(get_uow)) -> MaintenanceService:
    return MaintenanceService(uow=uow, event_dispatcher=dispatcher)


def get_inventory_service(uow: UnitOfWork = Depends(get_uow)) -> InventoryService:
    return InventoryService(uow=uow, event_dispatcher=dispatcher)


def get_procurement_service(uow: UnitOfWork = Depends(get_uow)) -> ProcurementService:
    return ProcurementService(uow=uow, event_dispatcher=dispatcher)


def get_finance_service(uow: UnitOfWork = Depends(get_uow)) -> FinanceService:
    return FinanceService(uow=uow, event_dispatcher=dispatcher)


def get_analytics_service(db: AsyncSession = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db=db)


# ---------------------------------------------------------------------------
# Supabase Service
# ---------------------------------------------------------------------------
from app.services.supabase_service import SupabaseService, get_supabase_service  # noqa: E402


def get_supabase(supabase: SupabaseService = Depends(get_supabase_service)) -> SupabaseService:
    return supabase


# ---------------------------------------------------------------------------
# Authorization helpers — pass-through in evaluation mode
# ---------------------------------------------------------------------------
