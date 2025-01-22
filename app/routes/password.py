from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.data.utils.database import get_db
from app.data.schemas.password_schemas import (
    ForgotPasswordRequest, SetNewPassword,
    PasswordResetResponse
)
from app.service.password_service import PasswordResetService

class PasswordResetRouter:
    def __init__(self):
        self.router = APIRouter(
            prefix="/auth/password",
            tags=["authentication"]
        )
        self._register_routes()

    def _register_routes(self):
        @self.router.post("/forgot", response_model=PasswordResetResponse)
        async def forgot_password(
            request: ForgotPasswordRequest,
            db: Session = Depends(get_db)
        ):
            """Request password reset link"""
            service = PasswordResetService(session=db)
            result = await service.request_password_reset(request)
            return result

        @self.router.post("/reset", response_model=PasswordResetResponse)
        async def reset_password(
            reset_data: SetNewPassword,
            db: Session = Depends(get_db)
        ):
            """Reset password using token"""
            service = PasswordResetService(session=db)
            result = await service.set_new_password(reset_data)
            return result


# Initialize router
password_reset_router = PasswordResetRouter().router