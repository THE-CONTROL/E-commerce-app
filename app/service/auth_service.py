from typing import Any, TypeVar
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.auth_handler import AuthHandler
from app.core.config import get_settings
from app.core.email_service import EmailService
from app.core.hash_helper import HashHelper
from app.data.models.admin_models import Admin
from app.data.models.user_models import User
from app.data.schemas.auth_schemas import (
    AdminCreate, RefreshRequest, TokenResponse, UserCreate, UserLogin, UserWithToken
)
from app.repository.auth_repo import UserAuthRepository, AdminAuthRepository
from app.service.base_service import BaseService

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
SchemaType = TypeVar("SchemaType")

class AuthBaseService(BaseService[ModelType, CreateSchemaType, SchemaType]):
    def __init__(self, repository: Any, session: Session):
        super().__init__(repository=repository)
        self.email_service = EmailService()
        self.settings = get_settings()
        self.session = session

    async def sign_in(self, user_data: UserLogin) -> TokenResponse:
        """Base authentication logic"""
        entity = self._repository.get_by_field("username", user_data.username)
        if not entity or entity.is_suspended:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
          
        if not HashHelper.verify_credential(user_data.password, entity.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
            
        self._repository.update_last_login(entity)
            
        token_data = AuthHandler.sign_jwt(user_id=entity.id)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to process request"
            )
            
        otp = self._repository.create_otp()
        
        await self.email_service.send_otp_email(
            email=entity.email,
            username=entity.username,
            otp=otp
        )
            
        return TokenResponse(
            message="Login successful",
            token=UserWithToken(**token_data)
        )

    def confirm_otp(self, otp: str) -> dict:
        """Check otp validity"""
        if not self._repository.check_otp(otp):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid otp {self._repository.check_otp(otp)}"
            )
        return {"message": "Validation successful"}
    
    def create_new_token(self, request: RefreshRequest) -> dict:
        """Create a new access token from refresh token"""
        new_access_token = AuthHandler.refresh_jwt(request.refresh_token)
        if not new_access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        return {"access_token": new_access_token}

class UserAuthService(AuthBaseService[User, UserCreate, SchemaType]):
    def __init__(self, session: Session):
        super().__init__(
            repository=UserAuthRepository(session=session),
            session=session
        )

    def sign_up(self, user_data: UserCreate) -> dict:
        """Register a new user"""
        if not self._repository.passwords_match(
            user_data.password,
            user_data.confirm_password
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match"
            )
            
        if self._repository.get_by_field("username", user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        user_dict = {
            "username": user_data.username,
            "password": HashHelper.hash_and_validate(user_data.password, credential_type="password"),
        }
        
        for field in ["first_name", "last_name", "email", "age", "address", "nin", "bvn"]:
            value = getattr(user_data, field, None)
            if value is not None:
                if field == "email":
                    self._repository.validate_email(field, value)
                elif field == "age":
                    self._repository.validate_age(field, value)
                user_dict[field] = value

        try:
            self.session.begin_nested()
            user_result = self._repository.create_entity(user_dict)
            self.session.commit()
            
            response = user_dict.copy()
            response.pop("password")
            response["id"] = user_result["id"]
            
            return response

        except Exception as e:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

class AdminAuthService(AuthBaseService[Admin, AdminCreate, SchemaType]):
    def __init__(self, session: Session):
        super().__init__(
            repository=AdminAuthRepository(session=session),
            session=session
        )

    def sign_up(self, user_data: AdminCreate) -> dict:
        """Register a new admin"""
        if not self._repository.passwords_match(
            user_data.password,
            user_data.confirm_password
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match"
            )
            
        if self._repository.get_by_field("username", user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        admin_dict = {
            "username": user_data.username,
            "password": HashHelper.hash_and_validate(user_data.password, credential_type="password"),
            "type": user_data.type
        }

        try:
            self.session.begin_nested()
            admin_result = self._repository.create_entity(admin_dict)
            self.session.commit()
            
            response = admin_dict.copy()
            response.pop("password")
            response["id"] = admin_result["id"]
            
            return response

        except Exception as e:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )