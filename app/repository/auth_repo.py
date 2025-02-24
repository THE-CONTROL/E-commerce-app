from typing import Any, Dict, TypeVar
from datetime import datetime, timezone
from app.core.config import TOTP
from app.data.models.admin_models import Admin
from app.data.models.user_models import User
from app.data.schemas.admin_schemas import AdminBase
from app.repository.base_repo import BaseRepository
from app.data.schemas.user_schemas import UserBase
from sqlalchemy.orm import Session
from app.repository.mixin import ValidationMixin

ModelType = TypeVar("ModelType")
SchemaType = TypeVar("SchemaType")

class AuthRepository(BaseRepository[ModelType, SchemaType], ValidationMixin):
    def __init__(self, model: type[ModelType], session: Session):
        super().__init__(model=model, session=session)

    def create_entity(self, data: Dict[str, Any]) -> Dict:
        """Create a new entity from dictionary data"""
        return self.create(data)
    
    def update_last_login(self, entity: ModelType) -> Dict:
        """Update entity's last login timestamp"""
        entity.last_login = datetime.now(timezone.utc)
        return self.update(entity)
    
    def create_otp(self) -> str:
        """Create the otp"""
        totp = TOTP.now()
        return totp
    
    def check_otp(self, code: str) -> bool:
        """Check the otp validity"""
        return TOTP.verify(code)

class UserAuthRepository(AuthRepository[User, UserBase]):
    def __init__(self, session: Session):
        super().__init__(model=User, session=session)

class AdminAuthRepository(AuthRepository[Admin, AdminBase]):
    def __init__(self, session: Session):
        super().__init__(model=Admin, session=session)