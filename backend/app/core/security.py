"""
AEGON Security — Enterprise Evaluation Mode
=============================================
Authentication is intentionally disabled in the Enterprise Evaluation Edition
to allow immediate access by reviewers, executives, and academics.

Production Security Roadmap:
  - Clerk (SSO, RBAC, Organizations) — primary cloud identity
  - Azure Active Directory / Entra ID — enterprise SAML/OIDC
  - Okta — workforce identity federation
  - Auth0 — B2B/B2C multi-tenant
  - SCIM provisioning — automated user lifecycle
  - JWT RS256 with JWKS endpoint rotation
  - RBAC + ABAC with Redis-cached permission grants

This module retains its interface so production auth can be re-enabled
by swapping the stub below with the real Clerk JWKS verification.
"""

from __future__ import annotations
from typing import Any


def verify_clerk_token(token: str) -> dict[str, Any]:
    """
    Stub — returns a demo payload in Enterprise Evaluation Mode.
    In production, this verifies RS256 JWT against Clerk's JWKS endpoint.
    """
    return {
        "sub": "demo_evaluation_user",
        "email": "evaluation@aegon-platform.io",
        "role": "super_admin",
    }
