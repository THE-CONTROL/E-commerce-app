from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.hash_helper import HashHelper
from app.data.schemas.password_schemas import UpdatePassword
from app.repository.account_repo import AccountRepository
from app.repository.user_repo import UserRepository
from app.service.base_service import BaseService
from app.data.models.user_models import User, UserTier
from app.data.schemas.user_schemas import PasscodeResponse, SetPasscode, UserBase, UserRead
from app.data.schemas.auth_schemas import UserCreate


class UserService(BaseService[User, UserCreate, UserBase]):
    def __init__(self, session: Session):
        super().__init__(repository=UserRepository(session=session))
        self.account_repository = AccountRepository(session=session)
        self.session = session
        
    def set_passcode(self, user_id: int, new_passcode: SetPasscode) -> Dict:
        """Set user passcode"""
        user = self.get_by_id(user_id)
        if not len(new_passcode.passcode) == 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passcode must be 4 characters"
            )
        if not new_passcode.isdigit():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passcode must contain only digits"
            )
        
        passcode = HashHelper.hash_and_validate(new_passcode.passcode, credential_type="passcode")
            
        return self._repository.set_new_passcode(user, passcode)
    
    def check_passcode(self, user_id: int, passcode_data: SetPasscode) -> dict: 
        """Check if the user passcode match and allow the user access"""
        user = self.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
          
        if not HashHelper.verify_credential(passcode_data.passcode, user.passcode):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
            
        return PasscodeResponse(
                    message="Code checked",
                    user=user
                )

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

    def _validate_filters(self, filters: Dict[str, Any]) -> None:
        """Validate filter parameters"""
        if 'tier' in filters and not isinstance(filters['tier'], UserTier):
            try:
                filters['tier'] = UserTier(filters['tier'])
            except ValueError:
                raise ValueError(f"Invalid tier value. Must be one of: {[t.value for t in UserTier]}")

        if 'age_range' in filters:
            if not isinstance(filters['age_range'], (list, tuple)) or len(filters['age_range']) != 2:
                raise ValueError("age_range must be a tuple of (min_age, max_age)")
            min_age, max_age = filters['age_range']
            if not (isinstance(min_age, int) and isinstance(max_age, int)):
                raise ValueError("Age values must be integers")
            if min_age < 0 or max_age < 0:
                raise ValueError("Age values cannot be negative")
            if min_age > max_age:
                raise ValueError("Minimum age cannot be greater than maximum age")

        if 'nin' in filters and not isinstance(filters['nin'], str):
            raise ValueError("NIN must be a string")
        
        if 'bvn' in filters and not isinstance(filters['bvn'], str):
            raise ValueError("BVN must be a string")