from sqlalchemy import TIMESTAMP, Boolean, Column, Integer, String, ForeignKey, DateTime, text
from datetime import datetime, timezone
from app.data.utils.database import Base


class PasswordReset(Base):
    __tablename__ = "password_resets"
    __table_args__ = {'comment': 'Stores password reset tokens'}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    token = Column(String(255), nullable=False, unique=True, index=True)
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        comment='Token expiration timestamp'
    )
    used = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text('false'),
        comment='Whether the token has been used'
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text('now()'),
        comment='Token creation timestamp'
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text('now()'),
        onupdate=lambda: datetime.now(timezone.utc),
        comment='Last update timestamp'
    )