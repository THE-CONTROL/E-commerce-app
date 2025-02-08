from sqlalchemy import TIMESTAMP, Boolean, Column, Integer, String, text, Enum, DateTime
from sqlalchemy.orm import relationship
from app.data.utils.database import Base
import enum
from datetime import datetime, timezone

# Enum for user tiers
class UserTier(str, enum.Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    VIP = "vip"
    

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'comment': 'Stores user account information'}

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Personal information
    first_name = Column(String(50), nullable=True, comment='User first name')
    last_name = Column(String(50), nullable=True, comment='User last name')
    username = Column(String(50), nullable=False, unique=True, index=True, 
                     comment='Unique username for login')
    password = Column(String(255), nullable=False, comment='Hashed password')
    passcode = Column(String(255), nullable=True, comment='Hashed password')
    
    # Contact and additional info
    age = Column(Integer, nullable=True, comment='User age')
    address = Column(String(255), nullable=True, comment='User address')
    email = Column(String(100), nullable=True, unique=True, index=True, 
                  comment='User email address')
    
    # Account type and verification
    tier = Column(
        Enum(UserTier),
        nullable=True,
        default=UserTier.BASIC,
        comment='User subscription tier'
    )
    
    # Nigerian-specific fields
    nin = Column(String(11), nullable=True, unique=True, index=True,
                comment='Nigerian National Identification Number')
    bvn = Column(String(11), nullable=True, unique=True, index=True,
                comment='Bank Verification Number')
    
    # Account status
    verified = Column(Boolean, default=False, nullable=False,
                     comment='User verification status')
    is_active = Column(Boolean, default=True, nullable=False,
                      comment='Account active status')
    
    # Timestamps
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

    # Relationships
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    stores = relationship("Store", back_populates="user", cascade="all, delete-orphan")
    
    def repr(self):
        """String representation of the user"""
        return f"<User {self.username}>"

    @property
    def full_name(self):
        """Return user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
