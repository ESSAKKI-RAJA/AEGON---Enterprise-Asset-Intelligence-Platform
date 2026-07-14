"""
AEGON Auth API — Enterprise Evaluation Edition
================================================
GET /auth/me — returns the static Enterprise Evaluation User profile.

The /sync endpoint (Clerk user upsert) is removed in evaluation mode.
In production, /sync is called on first login to register the Clerk user
in the AEGON database.
"""

from typing import Any
from fastapi import APIRouter

from app.core.demo_user import DEMO_USER

router = APIRouter()


@router.get("/me", response_model=dict)
async def get_me() -> Any:
    """
    Return the Enterprise Evaluation User profile.
    In production: requires valid Clerk Bearer token and returns DB user record.
    """
    return {
        "data": {
            "email": DEMO_USER.email,
            "first_name": DEMO_USER.first_name,
            "last_name": DEMO_USER.last_name,
            "is_active": DEMO_USER.is_active,
            "role": DEMO_USER.role_name,
            "department": DEMO_USER.department_name,
            "clerk_user_id": DEMO_USER.clerk_user_id,
            "evaluation_mode": True,
        }
    }
