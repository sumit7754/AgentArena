"""User repository for user-specific database operations."""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_

from .base_repository import BaseRepository
from ..models.user import User
from ..core.logger import get_logger

logger = get_logger(__name__)


class UserRepository(BaseRepository[User]):
    """Repository for user-specific database operations."""
    
    def __init__(self, db_session: AsyncSession):
        """Initialize the user repository."""
        super().__init__(db_session, User)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email address."""
        return await self.get_by_field("email", email)
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        return await self.get_by_field("username", username)
    
    async def get_by_email_or_username(self, email_or_username: str) -> Optional[User]:
        """Get a user by email or username."""
        try:
            result = await self.db.execute(
                select(User).filter(
                    or_(
                        User.email == email_or_username,
                        User.username == email_or_username
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching user by email or username: {e}")
            raise
    
    async def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all active users."""
        return await self.get_all(skip=skip, limit=limit, filters={"is_active": True})
    
    async def get_admin_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all admin users."""
        return await self.get_all(skip=skip, limit=limit, filters={"role": "admin"})
    
    async def email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        user = await self.get_by_email(email)
        return user is not None
    
    async def username_exists(self, username: str) -> bool:
        """Check if username already exists."""
        user = await self.get_by_username(username)
        return user is not None
    
    async def activate_user(self, user_id: int) -> User:
        """Activate a user account."""
        return await self.update(user_id, {"is_active": True})
    
    async def deactivate_user(self, user_id: int) -> User:
        """Deactivate a user account."""
        return await self.update(user_id, {"is_active": False})
    
    async def update_last_login(self, user_id: int) -> User:
        """Update the last login timestamp."""
        from datetime import datetime
        return await self.update(user_id, {"last_login": datetime.utcnow()})
    
    async def get_user_stats(self, user_id: int) -> dict:
        """Get user statistics."""
        try:
            # This would typically involve complex queries with joins
            # For now, returning a basic structure
            user = await self.get_by_id_or_404(user_id)
            
            stats = {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "created_at": user.created_at,
                "last_login": user.last_login,
                "is_active": user.is_active,
                # Additional stats can be added here
            }
            
            return stats
        except Exception as e:
            logger.error(f"Error fetching user stats for user {user_id}: {e}")
            raise