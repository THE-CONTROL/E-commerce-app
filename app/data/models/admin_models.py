from sqlalchemy import TIMESTAMP, Boolean, Column, Integer, String, text, Enum, DateTime
from app.data.utils.database import Base
import enum
from datetime import datetime, timezone


class AdminType(str, enum.Enum):
    REGULAR = "regular"
    SUPER = "super"
    

class Admin(Base):
    __tablename__ = "admins"
    __table_args__ = {'comment': 'Stores admin account information'}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True, index=True, 
                     comment='Unique username for login')
    password = Column(String(255), nullable=False, comment='Hashed password')
    email = Column(String(100), nullable=True, unique=True, index=True, 
                  comment='User email address')
    type = Column(
        Enum(AdminType),
        nullable=True,
        default=AdminType.REGULAR,
        comment='The type of admin'
    )
    is_active = Column(Boolean, default=True, nullable=False,
                      comment='Account active status')
    date_joined = Column(
        TIMESTAMP(timezone=True),
        server_default=text('now()'),
        nullable=False,
        comment='Account creation timestamp'
    )
    last_login = Column(
        DateTime(timezone=True),
        nullable=True,
        comment='Last login timestamp'
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text('now()'),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment='Last update timestamp'
    )
    
    def __repr__(self):  # Fixed repr method name
        """String representation of the admin"""
        return f"<Admin {self.username}>"
