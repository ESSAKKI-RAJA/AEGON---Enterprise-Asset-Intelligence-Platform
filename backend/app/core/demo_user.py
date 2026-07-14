"""
AEGON Demo User — Enterprise Evaluation Edition
================================================
This module defines the static Enterprise Evaluation User that is injected
into all dependency-injection points in demo mode.

Production deployments replace this with real Clerk JWT verification,
Azure AD, Okta, or Auth0 integration. See README > Authentication Roadmap.
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
    clerk_user_id: Optional[str] = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def initials(self) -> str:
        return "EE"


# Singleton instance used by all deps
DEMO_USER = DemoUser()
