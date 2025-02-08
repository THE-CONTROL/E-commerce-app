from typing import Dict, List, Optional
from datetime import datetime, timezone
from app.data.models.admin_models import Admin, AdminType
from app.repository.base_repo import BaseRepository
from app.data.schemas.admin_schemas import AdminBase
from sqlalchemy.orm import Session
from app.repository.mixin import ValidationMixin


class AdminRepository(BaseRepository[Admin, AdminBase], ValidationMixin):
    def __init__(self, session: Session):
        super().__init__(model=Admin, session=session)
    
    def get_admin_by_id(self, admin_id: int) -> Optional[Admin]:
        return self.get_by_field("id", admin_id)
    
    def get_admin_by_email(self, email: str) -> Optional[Admin]:  # Fixed typo in method name
        return self.get_by_field("email", email)
    
    def get_admin_by_username(self, username: str) -> Optional[Admin]:
        return self.get_by_field("username", username)

    def change_password(self, admin: Admin) -> Dict:
        return self.update(admin)

    def deactivate_account(self, admin: Admin) -> Dict:
        """Deactivate admin account"""
        admin.is_active = False
        admin.updated_at = datetime.now(timezone.utc)
        return self.update(admin)

    def activate_account(self, admin: Admin) -> Dict:
        """Activate admin account"""
        admin.is_active = True
        admin.updated_at = datetime.now(timezone.utc)
        return self.update(admin)

    def update_type(self, admin: Admin, new_type: AdminType) -> Dict:  # Fixed method name from update_tier
        """Update admin type"""
        admin.type = new_type
        admin.updated_at = datetime.now(timezone.utc)
        return self.update(admin)
    
    def list_admins(self, skip: int = 0, limit: int = 100) -> List[Admin]:
        try:
            query = self.session.query(self.model)\
                .order_by(self.model.id.asc())\
                .offset(skip)\
                .limit(limit)\
                .all()
            return query
        except Exception as e:
            self.session.rollback()
            raise e
