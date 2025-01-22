from fastapi import Depends
from app.data.schemas.auth_schemas import RefreshRequest, RefreshResponse, TokenResponse, UserCreate, UserLogin
from app.data.schemas.user_schemas import UserBase
from app.data.utils.database import get_db
from app.data.models.user_models import User
from app.routes.base import BaseRouter
from app.service.auth_service import AuthService
from sqlalchemy.orm import Session


# Auth Router (public routes)
class AuthRouter(BaseRouter[User, UserCreate, UserBase, AuthService]):
    def __init__(self):
        super().__init__(
            service_class=AuthService,
            prefix="/auth",
            tags=["auth"],
            protected=False
        )
        self._register_auth_routes()

    def _register_auth_routes(self):
        @self.router.post("/register", response_model=dict)
        async def register(user: UserCreate, db: Session = Depends(get_db)):
            try:
                return self.service_class(session=db).sign_up(user_data=user)
            except Exception as error:
                raise error

        @self.router.post("/login", response_model=TokenResponse)
        async def login(user: UserLogin, db: Session = Depends(get_db)):
            try:
                return self.service_class(session=db).sign_in(user_data=user)
            except Exception as error:
                raise error

        @self.router.post("/refresh", response_model=RefreshResponse)
        async def refresh(request: RefreshRequest, db: Session = Depends(get_db)):
            try:
                return self.service_class(session=db).create_new_token(request=request)
            except Exception as error:
                raise error
            
            
# Initialize router
auth_router = AuthRouter().router