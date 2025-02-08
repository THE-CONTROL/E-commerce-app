from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy import and_
from sqlalchemy.orm import Session
from app.data.models.user_models import User
from app.data.models.password_models import PasswordReset
from app.repository.base_repo import BaseRepository
from app.core.hash_helper import HashHelper

class PasswordResetRepository(BaseRepository[PasswordReset, None]):
    def __init__(self, session: Session):
        super().__init__(model=PasswordReset, session=session)

    def create_reset_token(self, user_id: int, token: str) -> PasswordReset:
        """Create a new password reset token"""
        # Expire any existing tokens
        self.expire_existing_tokens(user_id)
        
        # Create new token with 1-hour expiry
        reset_token = PasswordReset(
            user_id=user_id,
            token=token,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        
        self.session.add(reset_token)
        self.session.commit()
        self.session.refresh(reset_token)
        return reset_token

    def get_valid_token(self, token: str) -> Optional[PasswordReset]:
        """Get a valid (non-expired) token"""
        return self.session.query(self.model).filter(
            and_(
                self.model.token == token,
                self.model.expires_at > datetime.now(timezone.utc),
                self.model.used.is_(False)
            )
        ).first()

    def expire_existing_tokens(self, user_id: int) -> None:
        """Expire all existing tokens for a user"""
        self.session.query(self.model).filter(
            and_(
                self.model.user_id == user_id,
                self.model.used.is_(False)
            )
        ).update({
            "expires_at": datetime.now(timezone.utc),
            "used": True
        })
        self.session.commit()

    def mark_token_used(self, token: PasswordReset) -> None:
        """Mark a token as used"""
        token.used = True
        token.updated_at = datetime.now(timezone.utc)
        self.session.add(token)
        self.session.commit()

    def reset_password(self, user: User, new_password: str) -> None:
        """Reset user's password"""
        user.password = HashHelper.hash_and_validate(new_password, credential_type="password")
        user.updated_at = datetime.now(timezone.utc)
        self.session.add(user)
        self.session.commit()