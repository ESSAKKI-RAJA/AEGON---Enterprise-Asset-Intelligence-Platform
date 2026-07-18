from typing import Optional
"""
AEGON Auth Service
===================
Supabase Auth is the identity provider. This service handles the server-side
user sync — creating or updating a local User record when a Supabase-authenticated
user first signs in.

All token generation, session management, and password handling are owned by
Supabase Auth. This service only manages the local user profile mirror.
"""

from typing import Optional

from app.services.base import BaseService, track_metrics
from app.repositories.base import UnitOfWork
from app.core.events import EventDispatcher
from app.models.identity import User
from app.models.enums import UserRole
from app.repositories.user import UserRepository, RoleRepository


class AuthService(BaseService):
    def __init__(self, uow: UnitOfWork, event_dispatcher: Optional[EventDispatcher] = None):
        super().__init__(uow, event_dispatcher)

    @track_metrics("sync_supabase_user")
    async def sync_supabase_user(
        self,
        *,
        supabase_user_id: str,
        email: str,
        first_name: str = "",
        last_name: str = "",
    ) -> User:
        """
        Upsert a Supabase-authenticated user into the AEGON local database.

        - If the user already exists (by supabase_user_id or email), update
          their profile fields and ensure supabase_user_id is set.
        - If the user does not exist, create a new record with the default
          VIEWER role — a Super Admin can promote them later.

        Returns the User record.
        """
        async def _operation():
            user_repo: UserRepository = self.uow.get_repository(UserRepository)

            # 1. Try lookup by Supabase user ID (primary)
            user: Optional[User] = await user_repo.get_by_supabase_user_id(supabase_user_id)

            # 2. Fall back to email (handles pre-migration users)
            if user is None:
                user = await user_repo.get_by_email(email)

            if user is not None:
                # Update profile and ensure supabase_user_id is stamped
                user.supabase_user_id = supabase_user_id
                user.first_name = first_name or user.first_name
                user.last_name = last_name or user.last_name
                user.email = email
                await user_repo.update(user)
                return user

            # 3. First-time Supabase sign-in — create the user
            role_repo = self.uow.get_repository(RoleRepository)
            viewer_role = await role_repo.get_by_name(UserRole.VIEWER)

            new_user = User(
                supabase_user_id=supabase_user_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                hashed_password=None,  # Supabase manages auth — no local password
                is_active=True,
                role_id=viewer_role.id if viewer_role else None,
            )
            await user_repo.create(new_user)
            return new_user

        return await self.execute_in_transaction(_operation)
