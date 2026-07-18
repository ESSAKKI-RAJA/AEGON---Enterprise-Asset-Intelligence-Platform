from typing import Optional
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user import UserRepository
from app.schemas.core import UserCreate
from app.models import User
from fastapi import HTTPException, status
from app.services.base import BaseService, track_metrics
from app.repositories.base import UnitOfWork
from app.core.events import EventDispatcher

class UserService(BaseService):
    def __init__(self, uow: UnitOfWork, event_dispatcher: Optional[EventDispatcher] = None):
        super().__init__(uow, event_dispatcher)

    @track_metrics("get_user_by_email")
    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        # db parameter is kept for backward compatibility with deps.py if needed,
        # but we use self.uow internally to align with the framework.
        async def _operation():
            repo = self.uow.get_repository(UserRepository)
            return await repo.get_by_email(email)
        return await self.execute_in_transaction(_operation)

    @track_metrics("create_user")
    async def create_user(self, db: AsyncSession, user_in: UserCreate) -> User:
        async def _operation():
            repo = self.uow.get_repository(UserRepository)
            existing_user = await repo.get_by_email(email=user_in.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="The user with this username already exists in the system.",
                )
            
            user = User(
                email=user_in.email,
                hashed_password=None,
                first_name=user_in.first_name,
                last_name=user_in.last_name,
                is_active=user_in.is_active,
                role_id=user_in.role_id,
                department_id=user_in.department_id,
            )
            return await repo.create(user)
        return await self.execute_in_transaction(_operation)
    
    @track_metrics("get_users")
    async def get_users(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        async def _operation():
            repo = self.uow.get_repository(UserRepository)
            page = (skip // limit) + 1 if limit > 0 else 1
            res = await repo.get_all(page=page, page_size=limit)
            return res.items
        return await self.execute_in_transaction(_operation)
