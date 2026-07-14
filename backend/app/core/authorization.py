"""
AEGON Authorization — Enterprise Evaluation Mode
=================================================
RBAC/ABAC is fully designed but bypassed in this evaluation edition.

In production:
  - require_permission: checks fine-grained DB permissions per role
  - require_role: enforces role hierarchy (viewer → operator → admin → super_admin)
  - require_department_access: ABAC data filtering by organizational unit

All checks pass-through to the demo user (super_admin) in this edition.
"""

from typing import List, Optional
from app.core.demo_user import DEMO_USER, DemoUser


def clear_permission_cache():
    """No-op in evaluation mode."""
    pass


class require_permission:
    """Pass-through in evaluation mode. In production: verifies DB role permissions."""

    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    async def __call__(self, *args, **kwargs) -> DemoUser:
        return DEMO_USER


class require_role:
    """Pass-through in evaluation mode. In production: enforces role hierarchy."""

    def __init__(self, allowed_roles: List):
        self.allowed_roles = allowed_roles

    async def __call__(self, *args, **kwargs) -> DemoUser:
        return DEMO_USER


def require_department_access():
    """
    ABAC pass-through — evaluation user sees all departments.
    In production: filters data to user's department unless admin/super_admin.
    """
    async def _dependency(*args, **kwargs) -> Optional[str]:
        return None  # None = no department filter = see everything

    return _dependency
