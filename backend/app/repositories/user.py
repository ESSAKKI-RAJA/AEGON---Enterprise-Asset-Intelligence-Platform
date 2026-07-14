from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository, translate_db_exception, CacheHook, AuditHook
from app.models import User, Role


class UserRepository(BaseRepository[User]):
    """User repository implementing specialized user query patterns."""
    
    def __init__(
        self,
        session: AsyncSession,
        cache_hook: Optional[CacheHook] = None,
        audit_hook: Optional[AuditHook] = None,
    ):
        super().__init__(
            session=session,
            model_class=User,
            cache_hook=cache_hook,
            audit_hook=audit_hook,
        )

    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by email, excluding soft deleted users."""
        from sqlalchemy.orm import selectinload
        try:
            stmt = select(self.model_class).options(
                selectinload(self.model_class.role),
                selectinload(self.model_class.department)
            ).where(
                self.model_class.email == email,
                self.model_class.is_deleted == False
            )
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            raise translate_db_exception(e)

    async def get_by_clerk_user_id(self, clerk_user_id: str) -> Optional[User]:
        """Retrieve a user by their Clerk user ID (sub claim), excluding soft deleted users."""
        from sqlalchemy.orm import selectinload
        try:
            stmt = select(self.model_class).options(
                selectinload(self.model_class.role),
                selectinload(self.model_class.department)
            ).where(
                self.model_class.clerk_user_id == clerk_user_id,
                self.model_class.is_deleted == False
            )
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            raise translate_db_exception(e)



class RoleRepository(BaseRepository[Role]):
    """Role repository."""
    
    def __init__(
        self,
        session: AsyncSession,
        cache_hook: Optional[CacheHook] = None,
        audit_hook: Optional[AuditHook] = None,
    ):
        super().__init__(
            session=session,
            model_class=Role,
            cache_hook=cache_hook,
            audit_hook=audit_hook,
        )
