from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from sqlalchemy import and_, or_
from app.data.models.user_models import User
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
        user.is_email_verified = True
        user.is_phone_verified = True
        return self.update(user)

    def deactivate_account(self, user: User) -> Dict:
        """Deactivate user account"""
        user.is_active = False
        return self.update(user)

    def activate_account(self, user: User) -> Dict:
        """Activate user account"""
        user.is_active = True
        return self.update(user)
    
    def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[User]:
        """
        Retrieve a filtered, paginated list of users.
        """
        query = self.session.query(self.model)
            
        if filters:
            filter_conditions = []
                
            # Handle special filters
            if 'verification_status' in filters:
                query = query.filter(
                    self.model.verified == filters['verification_status']
                )
                del filters['verification_status']
                
            # Handle exact matches for specific fields
            for field in ['email']:
                if field in filters:
                    filter_conditions.append(
                        getattr(self.model, field) == filters[field]
                    )
                    del filters[field]
                
            # Handle remaining filters
            for column, value in filters.items():
                if hasattr(self.model, column):
                    if isinstance(value, list):
                        filter_conditions.append(
                            getattr(self.model, column).in_(value)
                        )
                    else:
                        filter_conditions.append(
                            getattr(self.model, column) == value
                        )
                
            if filter_conditions:
                query = query.filter(and_(*filter_conditions))
            
        return query.order_by(self.model.id.asc())\
                .offset(skip)\
               .limit(limit)\
               .all()

    def search_users(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """
        Search users across multiple fields.
        """
        search_term = f"%{search_term}%"
        return self.session.query(self.model)\
            .filter(
                or_(
                    self.model.username.ilike(search_term),
                    self.model.email.ilike(search_term),
                    self.model.first_name.ilike(search_term),
                    self.model.last_name.ilike(search_term),
                )
            )\
            .order_by(self.model.id.asc())\
            .offset(skip)\
            .limit(limit)\
            .all()
            
    def toggle_user_status(self, user: User, is_active: bool, admin_id: int) -> User:
        """
        Toggle user's active status with admin tracking
        """
        try:
            user.is_active = is_active

            # Could add audit fields here if needed:
            # user.last_modified_by = admin_id
            
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            return user
        except Exception as e:
            self.session.rollback()
            raise e
    