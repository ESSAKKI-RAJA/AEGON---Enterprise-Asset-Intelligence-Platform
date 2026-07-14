from app.repositories.base import BaseRepository
from app.models.identity import UserSession, RefreshToken, LoginHistory, PasswordResetToken

class UserSessionRepository(BaseRepository[UserSession]):
    def __init__(self, session, **kwargs):
        super().__init__(session, UserSession, **kwargs)

class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session, **kwargs):
        super().__init__(session, RefreshToken, **kwargs)

class LoginHistoryRepository(BaseRepository[LoginHistory]):
    def __init__(self, session, **kwargs):
        super().__init__(session, LoginHistory, **kwargs)

class PasswordResetTokenRepository(BaseRepository[PasswordResetToken]):
    def __init__(self, session, **kwargs):
        super().__init__(session, PasswordResetToken, **kwargs)
