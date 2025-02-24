from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.hash_helper import HashHelper
from app.data.schemas.password_schemas import UpdatePassword
from app.repository.account_repo import AccountRepository
from app.repository.user_repo import UserRepository
from app.service.base_service import BaseService
from app.data.models.user_models import User
from app.data.schemas.user_schemas import UserBase, UserRead
from app.data.schemas.auth_schemas import UserCreate


class UserService(BaseService[User, UserCreate, UserBase]):
    def __init__(self, session: Session):
        super().__init__(repository=UserRepository(session=session))
        self.account_repository = AccountRepository(session=session)
        self.session = session
        
    def verify_account(self, user_id: int) -> Dict:
        """Verify user account"""
        user = self.get_by_id(user_id)
        return self._repository.verify_account(user)

    def deactivate_account(self, user_id: int) -> Dict:
        """Deactivate user account"""
        user = self.get_by_id(user_id)
        return self._repository.deactivate_account(user)

    def activate_account(self, user_id: int) -> Dict:
        """Activate user account"""
        user = self.get_by_id(user_id)
        return self._repository.activate_account(user)

    def get_user_accounts(self, user_id: int) -> List[Dict]:
        """Get all accounts for a user"""
        user = self.get_by_id(user_id)
        accounts = self.account_repository.get_user_accounts(user_id)
        
        return [
            {
                "id": account.id,
                "account_number": account.account_number,
                "currency": account.currency.value,
                "balance": float(account.balance),
                "is_default": account.is_default
            }
            for account in accounts
        ]

    def change_password(self, user_id: int, password_data: UpdatePassword) -> Dict:
        """Change user password"""
        user = self.get_by_id(user_id)
        
        if not self._repository.passwords_match(
            password_data.password,
            password_data.confirm_password
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match"
            )
            
        user.password = HashHelper.hash_and_validate(password_data.password, credential_type="password")
        return self._repository.change_password(user)
    
    def list_filtered_users(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        search_term: Optional[str] = None
    ) -> List[UserRead]:
        """
        Get a filtered, paginated list of users.
        """
        try:
            # Validate pagination parameters
            if skip < 0:
                raise ValueError("Skip value cannot be negative")
            if limit < 1:
                raise ValueError("Limit must be greater than 0")
            if limit > 100:
                limit = 100
            
            # Validate filters if present
            if filters:
                self._validate_filters(filters)
            
            if search_term:
                users = self._repository.search_users(
                    search_term=search_term,
                    skip=skip,
                    limit=limit
                )
            else:
                users = self._repository.list_users(
                    skip=skip,
                    limit=limit,
                    filters=filters
                )
            
            return [UserRead.model_validate(user) for user in users]
            
        except ValueError as ve:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(ve)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving user list"
            )
            