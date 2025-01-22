from typing import Dict, Optional
from datetime import datetime, timezone
from app.data.models.user_models import User, UserTier
from app.repository.base_repo import BaseRepository
from app.data.schemas.user_schemas import UserBase
from sqlalchemy.orm import Session
from app.repository.mixin import ValidationMixin


class UserRepository(BaseRepository[User, UserBase], ValidationMixin):
    def __init__(self, session: Session):
        super().__init__(model=User, session=session)
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.get_by_field("id", user_id)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.get_by_field("email", email)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.get_by_field("username", username)

    def change_password(self, user: User) -> Dict:
        return self.update(user)

    def verify_account(self, user: User) -> Dict:
        """Mark user account as verified"""
        user.verified = True
        user.updated_at = datetime.now(timezone.utc)
        return self.update(user)

    def deactivate_account(self, user: User) -> Dict:
        """Deactivate user account"""
        user.is_active = False
        user.updated_at = datetime.now(timezone.utc)
        return self.update(user)

    def activate_account(self, user: User) -> Dict:
        """Activate user account"""
        user.is_active = True
        user.updated_at = datetime.now(timezone.utc)
        return self.update(user)

    def update_tier(self, user: User, new_tier: UserTier) -> Dict:
        """Update user subscription tier"""
        user.tier = new_tier
        user.updated_at = datetime.now(timezone.utc)
        return self.update(user)
    