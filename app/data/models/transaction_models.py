# app/data/models/transaction_models.py
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.data.utils.database import Base

class TransactionType(str, enum.Enum):
    CREDIT = "credit"
    DEBIT = "debit"
    WITHDRAWAL = "withdrawal"
    PRODUCT_PAYMENT = "product_payment"
    SUBSCRIPTION = "subscription"
    FEE = "fee"

class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    fee_amount = Column(Numeric(10, 2), default=0)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False, default=TransactionStatus.PENDING)
    reference = Column(String, unique=True, nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    virtual_account_id = Column(Integer, ForeignKey("virtual_bank_accounts.id"), nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    account = relationship("Account", back_populates="transactions")
    virtual_account = relationship("VirtualBankAccount")
