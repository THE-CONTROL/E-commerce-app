from fastapi import HTTPException, status
import secrets
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.email_service import EmailService
from app.data.models.user_models import User
from app.repository.password_repo import PasswordResetRepository
from app.data.schemas.password_schemas import (
    ForgotPasswordRequest, SetNewPassword, PasswordResetResponse
)

class PasswordResetService:
    def __init__(self, session: Session):
        self.session = session
        self.reset_repo = PasswordResetRepository(session)
        self.email_service = EmailService()
        self.settings = get_settings()

    async def request_password_reset(
        self, request: ForgotPasswordRequest
    ) -> PasswordResetResponse:
        """Handle forgot password request"""
        try:
            # Find user by email
            user = self.session.query(User).filter(User.email == request.email).first()
            if not user:
                # Return success even if email not found (security best practice)
                return PasswordResetResponse(
                    message="If your email is registered, you will receive a password reset link"
                )

            # Generate secure token
            token = secrets.token_urlsafe(32)
            
            # Create reset token
            reset_token = self.reset_repo.create_reset_token(user.id, token)
            
            # Generate reset link using config
            reset_link = self.settings.get_password_reset_link(token)
            
            # Send email with reset link
            await self.email_service.send_password_reset_email(
                email=user.email,
                username=user.username,
                reset_link=reset_link
            )
            
            return PasswordResetResponse(
                message="Password reset instructions have been sent to your email",
                email=user.email
            )
            
        except Exception as e:
            # Log error here
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def set_new_password(self, reset_data: SetNewPassword) -> PasswordResetResponse:
        """Set new password using reset token"""
        try:
            # Validate token
            reset_token = self.reset_repo.get_valid_token(reset_data.token)
            if not reset_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired reset token"
                )

            # Get user
            user = self.session.query(User).get(reset_token.user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            # Reset password
            self.reset_repo.reset_password(user, reset_data.password)
            
            # Mark token as used
            self.reset_repo.mark_token_used(reset_token)
            
            return PasswordResetResponse(
                message="Password has been reset successfully"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )