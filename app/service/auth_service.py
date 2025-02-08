from typing import Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.auth_handler import AuthHandler
from app.core.hash_helper import HashHelper
from app.data.models.admin_models import Admin
from app.repository.account_repo import AccountRepository
from app.repository.auth_repo import AuthRepository
from app.service.base_service import BaseService
from app.data.models.user_models import User, UserTier
from app.data.schemas.auth_schemas import (
    RefreshRequest, TokenResponse, UserCreate, UserLogin, UserWithToken
)
from app.data.schemas.user_schemas import UserBase


class AuthService(BaseService[User, UserCreate, UserBase]):
    def __init__(self, session: Session):
        super().__init__(repository=AuthRepository(session=session))
        self.account_repository = AccountRepository(session=session)
        self.session = session

    def sign_up(self, user_data: UserCreate) -> dict:
        """Register a new user with currency accounts"""
        # Password validation
        if not self._repository.passwords_match(
            user_data.password,
            user_data.confirm_password
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match"
            )
            
        # Check username uniqueness
        if self._repository.get_by_field("username", user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        # Create user with hashed password
        user_dict = {
            "username": user_data.username,
            "password": HashHelper.hash_and_validate(user_data.password, credential_type="password"),
            "tier": UserTier.BASIC
        }
        
        # Add optional fields if they exist
        for field in ["first_name", "last_name", "email", "age", "address", "nin", "bvn"]:
            value = getattr(user_data, field, None)
            if value is not None:
                if field == "email":
                    self._repository.validate_email(field, value)
                elif field == "age":
                    self._repository.validate_age(field, value)
                user_dict[field] = value

        try:
            # Begin transaction
            self.session.begin_nested()
            
            # Create user
            user_result = self._repository.create_user(user_dict)
            
            # Create currency accounts
            accounts = self.account_repository.create_user_accounts(user_result["id"])
            
            # Commit transaction
            self.session.commit()
            
            # Prepare response
            response = user_dict.copy()
            response.pop("password")
            response["id"] = user_result["id"]
            response["accounts"] = [
                {
                    "account_number": acc["account_number"],
                    "currency": acc["currency"].value,
                    "is_default": acc["is_default"]
                }
                for acc in accounts
            ]
            
            return response

        except Exception as e:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    def sign_in(self, user_data: UserLogin) -> dict:
        """Authenticate a user and update last login"""
        user = self._repository.get_by_field("username", user_data.username)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
          
        if not HashHelper.verify_credential(user_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
            
        # Update last login
        self._repository.update_last_login(user)
            
        token_data = AuthHandler.sign_jwt(user_id=user.id)
        if not token_data: 
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to process request"
            )
            
        return TokenResponse(
                    message="Login successful",
                    token=UserWithToken(**token_data)
                )
    
    def create_new_token(self, request: RefreshRequest) -> dict:
        """Create a new access token from refresh token"""
        new_access_token = AuthHandler.refresh_jwt(request.refresh_token)
        if not new_access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        return {
            "access_token": new_access_token
        }
        

class AdminAuthService(AuthService):
    def __init__(self, session: Session):
        super().__init__(session)
        self.model = Admin  # Use Admin model instead of User

    def sign_up(self, user_data: Any) -> dict:
        # Add any admin-specific signup logic here
        return super().sign_up(user_data)

    def sign_in(self, user_data: Any) -> dict:
        # Add any admin-specific signin logic here
        return super().sign_in(user_data)

    def create_new_token(self, request: Any) -> dict:
        # Add any admin-specific token refresh logic here
        return super().create_new_token(request)

    def _hash_password(self, password: str) -> str:
        # You can override password hashing if needed for admin accounts
        return super()._hash_password(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        # You can override password verification if needed for admin accounts
        return super()._verify_password(plain_password, hashed_password)