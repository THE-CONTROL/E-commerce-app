from fastapi import Depends, HTTPException
from enum import Enum
from app.data.models.admin_models import Admin
from app.data.schemas.admin_schemas import AdminBase
from app.data.schemas.auth_schemas import (
    RefreshRequest,
    RefreshResponse,
    TokenResponse,
    UserCreate,
    UserLogin,
    AdminCreate
)
from app.data.schemas.user_schemas import UserBase
from app.data.utils.database import get_db
from app.data.models.user_models import User
from app.routes.base import BaseRouter
from app.service.auth_service import AuthService, AdminAuthService
from sqlalchemy.orm import Session
from typing import Union, Type

class AuthType(str, Enum):
    USER = "user"
    ADMIN = "admin"

class AuthRouter(BaseRouter[Union[User, Admin], Union[UserCreate, AdminCreate], Union[UserBase, AdminBase], Union[AuthService, AdminAuthService]]):
    def __init__(self):
        super().__init__(
            service_class=AuthService,  # Default to user service
            prefix="/auth",
            tags=["auth"],
            protected=False
        )
        self._register_auth_routes()

    def get_service_class(self, auth_type: AuthType) -> Type[Union[AuthService, AdminAuthService]]:
        if auth_type == AuthType.USER:
            return AuthService
        elif auth_type == AuthType.ADMIN:
            return AdminAuthService
        raise HTTPException(status_code=400, detail="Invalid authentication type")

    def _register_auth_routes(self):
        @self.router.post("/{auth_type}/register", response_model=dict)
        async def register(
            auth_type: AuthType,
            user: Union[UserCreate, AdminCreate],
            db: Session = Depends(get_db)
        ):
            try:
                service_class = self.get_service_class(auth_type)
                return service_class(session=db).sign_up(user_data=user)
            except Exception as error:
                raise error

        @self.router.post("/{auth_type}/login", response_model=TokenResponse)
        async def login(
            auth_type: AuthType,
            user: Union[UserLogin, UserLogin],
            db: Session = Depends(get_db)
        ):
            try:
                service_class = self.get_service_class(auth_type)
                return service_class(session=db).sign_in(user_data=user)
            except Exception as error:
                raise error

        @self.router.post("/{auth_type}/refresh", response_model=RefreshResponse)
        async def refresh(
            auth_type: AuthType,
            request: RefreshRequest,
            db: Session = Depends(get_db)
        ):
            try:
                service_class = self.get_service_class(auth_type)
                return service_class(session=db).create_new_token(request=request)
            except Exception as error:
                raise error

# Initialize router
auth_router = AuthRouter().router