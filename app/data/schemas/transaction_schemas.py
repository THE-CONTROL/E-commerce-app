# app/data/schemas/transaction_schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from .account_schemas import AccountRead

class TransactionBase(BaseModel):
    type: str
    amount: Decimal
    description: Optional[str] = None

class TransactionCreate(TransactionBase):
    account_id: int
    status: str = "pending"

class TransactionUpdate(BaseModel):
    status: Optional[str] = None
    completed_at: Optional[datetime] = None

class TransactionRead(TransactionBase):
    id: int
    fee_amount: Decimal
    status: str
    reference: str
    account_id: int
    virtual_account_id: Optional[int]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    account: Optional[AccountRead]

    class Config:
        from_attributes = True

class TransactionListResponse(BaseModel):
    message: str
    data: List[TransactionRead]
    total: int
    page: int
    size: int

class TransactionResponse(BaseModel):
    message: str
    data: TransactionRead

class FundAccountRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = None
    return_url: Optional[str] = None

class WithdrawalRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = None