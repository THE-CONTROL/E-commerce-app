from sqlalchemy import TIMESTAMP, Boolean, Column, Integer, String, text, Enum, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.data.utils.database import Base
import enum
from datetime import datetime
from typing import List


# Enum for currencies
class Currency(str, enum.Enum):
    NGN = "NGN"  # Nigerian Naira
    USD = "USD"  # US Dollar
    EUR = "EUR"  # Euro
    GBP = "GBP"  # British Pound
    # Add more currencies as needed
    

class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = {'comment': 'Stores user currency accounts'}

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to user
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Account details
    currency = Column(
        Enum(Currency),
        nullable=False,
        comment='Account currency type'
    )
    account_number = Column(String(20), unique=True, nullable=False, index=True,
                          comment='Unique account number')
    balance = Column(Numeric(precision=20, scale=4), nullable=False, default=0,
                    comment='Current account balance')
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False,
                      comment='Account active status')
    is_default = Column(Boolean, default=False, nullable=False,
                       comment='Whether this is the default account for the currency')
    
    # Timestamps
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text('now()'),
        nullable=False,
        comment='Account creation timestamp'
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text('now()'),
        onupdate=datetime.utcnow,
        nullable=False,
        comment='Last update timestamp'
    )

    # Relationships
    user = relationship("User", back_populates="accounts")

    def __repr__(self):
        return f"<Account {self.account_number} ({self.currency})>"
