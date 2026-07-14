"""
AEGON Auth Service
===================
Clerk is the sole identity provider. This service handles only the
server-side user sync — creating or updating a local User record when
a Clerk-authenticated user first signs in.

All token generation, session management, and password handling have been
removed. Those concerns are owned by Clerk.
"""

from typing import Optional
from fastapi import HTTPException, status

from app.services.base import BaseService, track_metrics
from app.repositories.base import UnitOfWork
from app.core.events import EventDispatcher
from app.models.identity import User
from app.models.enums import UserRole
from app.repositories.user import UserRepository


class AuthService(BaseService):
    def __init__(self, uow: UnitOfWork, event_dispatcher: EventDispatcher = None):
        super().__init__(uow, event_dispatcher)

    @track_metrics("sync_clerk_user")
    async def sync_clerk_user(
        self,
        *,
        clerk_user_id: str,
        email: str,
        first_name: str = "",
        last_name: str = "",
    ) -> User:
        """
        Upsert a Clerk-authenticated user into the AEGON local database.

        - If the user already exists (by clerk_user_id or email), update their
          profile fields and ensure clerk_user_id is set.
        - If the user does not exist, create a new record with the default
          VIEWER role — a Super Admin can promote them later.

        Returns the User record.
        """
        async def _operation():
            user_repo: UserRepository = self.uow.get_repository(UserRepository)

            # 1. Try lookup by Clerk user ID (primary)
            user: Optional[User] = await user_repo.get_by_clerk_user_id(clerk_user_id)

            # 2. Fall back to email (handles pre-migration users)
            if user is None:
                user = await user_repo.get_by_email(email)

            if user is not None:
                # Update profile and ensure clerk_user_id is stamped
                user.clerk_user_id = clerk_user_id
                user.first_name = first_name or user.first_name
                user.last_name = last_name or user.last_name
                user.email = email
                await user_repo.update(user)
                return user

            # 3. First-time Clerk sign-in — create the user
            # Resolve the default VIEWER role
            from sqlalchemy import select
            from app.models.identity import Role
            from app.repositories.base import UnitOfWork  # noqa (already imported)

            # We need the DB session from the UoW to query the role
            db = self.uow._db  # type: ignore[attr-defined]
            from sqlalchemy import select as sa_select
            result = await db.execute(
                sa_select(Role).where(Role.name == UserRole.VIEWER)
            )
            viewer_role = result.scalar_one_or_none()

            new_user = User(
                clerk_user_id=clerk_user_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                hashed_password=None,  # Clerk manages auth — no local password
                is_active=True,
                role_id=viewer_role.id if viewer_role else None,
            )
            await user_repo.create(new_user)
            return new_user

        return await self.execute_in_transaction(_operation)
