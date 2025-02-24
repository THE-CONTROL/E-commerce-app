from fastapi import Depends, HTTPException, status
from app.data.schemas.auth_schemas import ProtectedUser
from app.data.schemas.user_schemas import UserRead, UserUpdate
from app.data.utils.database import get_db
from app.core.auth_dependency import get_current_user
from app.data.models.user_models import User
from app.routes.base import BaseRouter
from app.service.user_service import UserService
from sqlalchemy.orm import Session


class UserRouter(BaseRouter[User, UserRead, UserUpdate, UserService]):
    def __init__(self):
        super().__init__(
            service_class=UserService,
            prefix="/users",
            tags=["users"],
            protected=True
        )
        self._register_user_routes()

    def _register_user_routes(self):
        @self.router.get(
            "/me",
            response_model=UserRead,
            summary="Get current user information",
            description="Retrieve detailed information about the currently authenticated user"
        )
        async def get_current_user_info(
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user)
        ):
            try:
                return self.service_class(session=db).get_by_id(current_user.id)
            except Exception as error:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(error)
                )

        @self.router.put(
            "/me",
            response_model=UserRead,
            summary="Update current user",
            description="Update information for the currently authenticated user"
        )
        async def update_current_user(
            update_data: UserUpdate,
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user)
        ):
            try:
                return self.service_class(session=db).update(
                    id=current_user.id,
                    data=update_data
                )
            except Exception as error:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(error)
                )
            
        @self.router.put(
            "/me/verify",
            response_model=UserRead,
            summary="Verify user account",
            description="Verify the current user's account"
        )
        async def verify_account(
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user)
        ):
            try:
                return self.service_class(session=db).verify_account(current_user.id)
            except Exception as error:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(error)
                )

        @self.router.delete(
            "/me",
            response_model=UserRead,
            summary="Deactivate account",
            description="Deactivate the current user's account"
        )
        async def deactivate_account(
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user)
        ):
            try:
                return self.service_class(session=db).deactivate_account(current_user.id)
            except Exception as error:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(error)
                )


# Initialize router
user_router = UserRouter().router