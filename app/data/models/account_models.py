# app/data/models/account_models.py
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.data.utils.database import Base
import enum

class AccountType(str, enum.Enum):
    USER = "user"
    STORE = "store"
    PLATFORM = "platform"

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)
    key = Column(String, unique=True, nullable=False)
    balance = Column(Numeric(10, 2), default=0)
    currency = Column(String, default="NGN")
    is_fundable = Column(Boolean, default=True)
    is_withdrawable = Column(Boolean, default=True)
    is_suspended = Column(Boolean, default=False)
    locked = Column(Boolean, default=False)
    lock_reason = Column(String, nullable=True)
    locked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="accounts")
    virtual_accounts = relationship("VirtualBankAccount", back_populates="account")
    transactions = relationship("Transaction", back_populates="account")

class VirtualBankAccount(Base):
    __tablename__ = "virtual_bank_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    account_number = Column(String, unique=True, nullable=False)
    account_name = Column(String, nullable=False)
    bank_name = Column(String, nullable=False)
    bank_code = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    reference = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    account = relationship("Account", back_populates="virtual_accounts")
    user = relationship("User")