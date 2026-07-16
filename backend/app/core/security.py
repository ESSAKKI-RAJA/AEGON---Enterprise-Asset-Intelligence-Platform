"""
AEGON Security — Supabase JWT Verification
============================================
Authentication uses Supabase as the identity provider.

Production Security:
  - Supabase Auth — RS256 JWT via JWKS endpoint
  - JWT verification against SUPABASE_JWKS_URL
  - RBAC + ABAC with Redis-cached permission grants

This module provides JWT verification compatible with Supabase-issued tokens.
In Enterprise Evaluation Mode, a static demo payload is returned without
network calls, so reviewers can access the platform immediately.
"""

from __future__ import annotations
from typing import Any
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


def verify_supabase_token(token: str) -> dict[str, Any]:
    """
    Verifies a Supabase RS256 JWT against the SUPABASE_JWKS_URL.

    Enterprise Evaluation Mode: Returns a static demo payload without
    performing actual JWKS verification. Swap the body of this function
    with a real PyJWT + JWKS fetch (e.g. via `python-jose`) to enable
    production authentication.
    """
    # --- EVALUATION STUB ---
    # In production, implement JWKS verification:
    #
    #   from jose import jwt, jwk
    #   import httpx
    #   jwks = httpx.get(settings.SUPABASE_JWKS_URL).json()
    #   claims = jwt.decode(token, jwks, algorithms=["RS256"],
    #                       audience="authenticated")
    #   return claims
    #
    # -----------------------
    logger.debug("JWT verification in evaluation mode — returning demo payload.")
    return {
        "sub": "00000000-0000-0000-0000-000000000001",
        "email": "evaluation@aegon-platform.io",
        "role": "super_admin",
        "aud": "authenticated",
    }
