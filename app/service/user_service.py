from typing import Dict, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.hash_helper import HashHelper
from app.repository.account_repo import AccountRepository
from app.repository.user_repo import UserRepository
from app.service.base_service import BaseService
from app.data.models.user_models import User, UserTier
from app.data.schemas.user_schemas import UpdatePassword, UserBase
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

    def update_tier(self, user_id: int, new_tier: UserTier) -> Dict:
        """Update user subscription tier"""
        user = self.get_by_id(user_id)
        return self._repository.update_tier(user, new_tier)

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
            
        user.password = HashHelper.get_password_hash(password_data.password)
        return self._repository.change_password(user)