from __future__ import annotations
# Backwards compatibility shim — canonical definitions live in identity.py and organization.py
from app.models.identity import User, Role
from app.models.organization import Department

__all__ = ["User", "Role", "Department"]
