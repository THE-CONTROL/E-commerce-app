from fastapi import Depends, HTTPException
from enum import Enum
from app.data.schemas.auth_schemas import (
    RefreshRequest,
    RefreshResponse,
    TokenResponse,
    UserCreate,
    UserLogin,
    AdminCreate
)
from app.data.utils.database import get_db
from app.routes.base import BaseRouter
from app.service.auth_service import UserAuthService, AdminAuthService
from sqlalchemy.orm import Session
from typing import Union, Type

class AuthType(str, Enum):
    USER = "user"
    ADMIN = "admin"

class AuthRouter(BaseRouter):
    def __init__(self):
        super().__init__(service_class=UserAuthService, prefix="/auth", tags=["auth"], protected=False)
        self._register_auth_routes()

    def get_service_class(self, auth_type: AuthType) -> Type[Union[UserAuthService, AdminAuthService]]:
        if auth_type == AuthType.USER:
            return UserAuthService
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
            service_class = self.get_service_class(auth_type)
            return service_class(session=db).sign_up(user_data=user)

        @self.router.post("/{auth_type}/login", response_model=TokenResponse)
        async def login(
            auth_type: AuthType,
            user: UserLogin,
            db: Session = Depends(get_db)
        ):
            service_class = self.get_service_class(auth_type)
            return await service_class(session=db).sign_in(user_data=user)
            
        @self.router.post("/{auth_type}/check_otp/{otp}", response_model=dict)
        async def confirm_otp_validity(
            auth_type: AuthType,
            otp: str,
            db: Session = Depends(get_db)
        ):
            service_class = self.get_service_class(auth_type)
            return service_class(session=db).confirm_otp(otp=otp)

        @self.router.post("/{auth_type}/refresh", response_model=RefreshResponse)
        async def refresh(
            auth_type: AuthType,
            request: RefreshRequest,
            db: Session = Depends(get_db)
        ):
            service_class = self.get_service_class(auth_type)
            return service_class(session=db).create_new_token(request=request)

# Initialize router
auth_router = AuthRouter().router