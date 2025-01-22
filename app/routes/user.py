from fastapi import Depends
from app.data.schemas.auth_schemas import ProtectedUser, UserCreate
from app.data.schemas.user_schemas import UserBase, UserRead
from app.data.utils.database import get_db
from app.core.auth_dependency import get_current_user
from app.data.models.user_models import User, UserTier
from app.routes.base import BaseRouter
from app.service.user_service import UserService
from sqlalchemy.orm import Session


# User Router (protected routes)
class UserRouter(BaseRouter[User, UserCreate, UserBase, UserService]):
    def __init__(self):
        super().__init__(
            service_class=UserService,
            prefix="/users",
            tags=["users"],
            protected=True
        )
        self._register_user_routes()

    def _register_user_routes(self):
        @self.router.get("/get", response_model=UserRead)
        async def get_current_user_info(
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user)
        ):
            try:
                return self.service_class(session=db).get_by_id(id=current_user.id)
            except Exception as error:
                raise error

        @self.router.put("/update", response_model=UserRead)
        async def update_current_user(
            update_data: UserBase,
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user)
        ):
            try:
                return self.service_class(session=db).update(
                    id=current_user.id,
                    data=update_data
                )
            except Exception as error:
                raise error
            
        @self.router.put("/verify", response_model=UserRead)
        def verify_account(
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user)
        ):
            """Verify user account"""
            try:
                return self.service_class(session=db).verify_account(current_user.id)
            except Exception as error:
                raise error

        @self.router.put("/tier/{tier}", response_model=UserRead)
        def update_user_tier(
            tier: UserTier,
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user)
        ):
            """Update user subscription tier"""
            try:
                return self.service_class(session=db).update_tier(current_user.id, tier)
            except Exception as error:
                raise error

        @self.router.delete("/delete", response_model=UserRead)
        def deactivate_account(
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user)
        ):
            """Deactivate user account"""
            try:
                return self.service_class(session=db).deactivate_account(current_user.id)
            except Exception as error:
                raise error
            

# Initialize router
user_router = UserRouter().router