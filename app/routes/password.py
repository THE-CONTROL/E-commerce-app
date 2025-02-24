from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.data.utils.database import get_db
from app.data.schemas.password_schemas import (
    ForgotPasswordRequest, SetNewPassword,
    PasswordResetResponse
)
from app.service.password_service import PasswordResetService
from app.routes.base import BaseRouter
from app.data.models.password_models import PasswordReset


class PasswordResetRouter(BaseRouter[PasswordReset, ForgotPasswordRequest, SetNewPassword, PasswordResetService]):
    def __init__(self):
        super().__init__(
            service_class=PasswordResetService,
            prefix="/auth/password",
            tags=["authentication"],
            protected=False  # Password reset routes should be public
        )
        self._register_password_routes()

    def _register_password_routes(self):
        @self.router.post(
            "/forgot",
            response_model=PasswordResetResponse,
            summary="Request password reset",
            description="Request a password reset link to be sent to email"
        )
        async def forgot_password(
            request: ForgotPasswordRequest,
            db: Session = Depends(get_db)
        ):
            """Request password reset link"""
            try:
                result = await self.service_class(session=db).request_password_reset(request)
                return result
            except Exception as error:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(error)
                )

        @self.router.post(
            "/reset",
            response_model=PasswordResetResponse,
            summary="Reset password",
            description="Reset password using the token received in email"
        )
        async def reset_password(
            reset_data: SetNewPassword,
            db: Session = Depends(get_db)
        ):
            """Reset password using token"""
            try:
                result = await self.service_class(session=db).set_new_password(reset_data)
                return result
            except Exception as error:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(error)
                )


# Initialize router
password_reset_router = PasswordResetRouter().router