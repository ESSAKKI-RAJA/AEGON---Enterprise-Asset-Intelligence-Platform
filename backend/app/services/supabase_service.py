"""
AEGON Supabase Service
========================
Central Supabase client abstraction for the FastAPI backend.

Provides access to:
  - Database (via Supabase REST or direct PostgreSQL)
  - Storage (file uploads, reports, inspection images)
  - Auth (admin-level user management)
  - Realtime (future — webhook triggers)

Architecture:
  - Registered in the DI container.
  - All services consume this abstraction — never instantiate supabase directly.
  - Secrets never leave the backend (SECRET_KEY only used server-side).
"""

from __future__ import annotations
from functools import lru_cache
from typing import Optional

from supabase import create_client, Client
from app.core.config import settings

import logging

logger = logging.getLogger(__name__)

# Storage bucket names — never hardcoded in callers, always via this service
BUCKET_INSPECTION_IMAGES = "inspection-images"
BUCKET_REPORTS = "reports"
BUCKET_ASSET_IMAGES = "asset-images"
BUCKET_DOCUMENTS = "documents"


class SupabaseService:
    """
    Centralised Supabase client. Wraps Database, Storage, and Auth operations.

    In production, this is the only place where the Supabase client is constructed.
    All other services receive it via Dependency Injection.
    """

    def __init__(self) -> None:
        self._client: Optional[Client] = None

    def _get_client(self) -> Client:
        if self._client is None:
            if not settings.SUPABASE_URL or not settings.SUPABASE_SECRET_KEY:
                raise RuntimeError("Supabase is not configured. Missing SUPABASE_URL or SUPABASE_SECRET_KEY.")
            self._client = create_client(
                supabase_url=settings.SUPABASE_URL,
                supabase_key=settings.SUPABASE_SECRET_KEY,
            )
            logger.info("Supabase client initialised for project: %s", settings.SUPABASE_URL)
        return self._client

    @property
    def client(self) -> Client:
        """Direct access to the underlying Supabase client (use sparingly)."""
        return self._get_client()

    # ---------------------------------------------------------------------------
    # Storage
    # ---------------------------------------------------------------------------

    def get_public_url(self, bucket: str, path: str) -> str:
        """Return the public URL for a stored file."""
        return self._get_client().storage.from_(bucket).get_public_url(path)

    def upload_file(self, bucket: str, path: str, data: bytes, content_type: str = "application/octet-stream") -> dict:
        """Upload a file to a Supabase Storage bucket. Returns the upload response."""
        return self._get_client().storage.from_(bucket).upload(
            path=path,
            file=data,
            file_options={"content-type": content_type},
        )

    def delete_file(self, bucket: str, paths: list[str]) -> dict:
        """Delete one or more files from a bucket."""
        return self._get_client().storage.from_(bucket).remove(paths)

    def upload_inspection_image(self, session_id: str, view_type: str, data: bytes) -> str:
        """Upload an inspection image and return its public URL."""
        path = f"{session_id}/{view_type}.jpg"
        self.upload_file(BUCKET_INSPECTION_IMAGES, path, data, "image/jpeg")
        return self.get_public_url(BUCKET_INSPECTION_IMAGES, path)

    def upload_report(self, session_id: str, filename: str, data: bytes) -> str:
        """Upload a generated report (PDF/Excel) and return its public URL."""
        path = f"{session_id}/{filename}"
        self.upload_file(BUCKET_REPORTS, path, data, "application/pdf")
        return self.get_public_url(BUCKET_REPORTS, path)

    # ---------------------------------------------------------------------------
    # Auth (Admin)
    # ---------------------------------------------------------------------------

    def get_user(self, supabase_user_id: str) -> dict:
        """Fetch a Supabase Auth user by their ID."""
        return self._get_client().auth.admin.get_user_by_id(supabase_user_id)

    def list_users(self) -> list:
        """List all users from Supabase Auth (admin only)."""
        return self._get_client().auth.admin.list_users()


@lru_cache(maxsize=1)
def get_supabase_service() -> SupabaseService:
    """
    Cached singleton factory for SupabaseService.
    Use as a FastAPI dependency: `Depends(get_supabase_service)`.
    """
    return SupabaseService()
