from typing import Any, Dict
from datetime import datetime, timezone
from app.data.models.user_models import User
from app.repository.base_repo import BaseRepository
from app.data.schemas.user_schemas import UserBase
from sqlalchemy.orm import Session
from app.repository.mixin import ValidationMixin


class AuthRepository(BaseRepository[User, UserBase], ValidationMixin):
    def __init__(self, session: Session):
        super().__init__(model=User, session=session)

    def create_user(self, user_data: Dict[str, Any]) -> Dict:
        """Create a new user from dictionary data"""
        return self.create(user_data)
    
    def update_last_login(self, user: User) -> Dict:
        """Update user's last login timestamp"""
        user.last_login = datetime.now(timezone.utc)
        return self.update(user)