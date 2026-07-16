"""
AEGON Demo User — Enterprise Evaluation Edition
================================================
This module defines the static Enterprise Evaluation User injected into all
dependency-injection points in evaluation mode.

Production deployments replace this with real Supabase Auth JWT verification.
See README > Authentication Roadmap.
"""

from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass(frozen=True)
class DemoUser:
    """Immutable demo user injected into all API dependency slots in evaluation mode."""

    id: uuid.UUID = field(default_factory=lambda: uuid.UUID("00000000-0000-0000-0000-000000000001"))
    email: str = "evaluation@aegon-platform.io"
    first_name: str = "Enterprise Evaluation"
    last_name: str = "User"
    role_name: str = "super_admin"
    department_name: str = "Executive Operations"
    is_active: bool = True
    # Supabase Auth user ID (the `sub` claim from Supabase JWTs)
    supabase_user_id: Optional[str] = "00000000-0000-0000-0000-000000000001"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def initials(self) -> str:
        return "EE"


# Singleton instance used by all deps
DEMO_USER = DemoUser()
