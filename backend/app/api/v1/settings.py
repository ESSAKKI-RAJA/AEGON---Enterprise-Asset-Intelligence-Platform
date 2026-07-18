from fastapi import APIRouter, Depends, Query
from typing import Any
from dependency_injector.wiring import Provide, inject

from app.services.user_service import UserService
from app.core.container import Container
from app.core.authorization import require_permission, require_role
from app.models.enums import UserRole
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

router = APIRouter()

@router.get("/users", response_model=dict, dependencies=[Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ADMIN]))])
@inject
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> Any:
    """
    Retrieve a list of users.
    Requires SUPER_ADMIN or ADMIN role.
    """
    users = await user_service.get_users(db, skip=skip, limit=limit)
    return {
        "data": [
            {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "role_id": str(user.role_id) if user.role_id else None,
                "department_id": str(user.department_id) if user.department_id else None,
            }
            for user in users
        ],
        "skip": skip,
        "limit": limit,
    }

@router.get("/roles", response_model=dict, dependencies=[Depends(require_permission("roles:read"))])
async def get_roles() -> Any:
    """
    Retrieve a list of available roles.
    Placeholder for actual RoleService call.
    """
    return {
        "data": [role.value for role in UserRole]
    }
