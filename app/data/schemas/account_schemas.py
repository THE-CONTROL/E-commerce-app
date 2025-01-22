from pydantic import BaseModel, Field, StringConstraints, field_validator
from typing_extensions import Annotated
from datetime import datetime
from decimal import Decimal
from enum import Enum
from app.data.models.account_models import Currency

# Custom string type with constraints
AccountNumberStr = Annotated[str, StringConstraints(min_length=10, max_length=10)]

class TransactionType(str, Enum):
    CREDIT = "credit"  # Adding money to account
    DEBIT = "debit"   # Removing money from account

class AccountBase(BaseModel):
    account_number: AccountNumberStr
    currency: Currency
    balance: Decimal = Field(default=0, ge=0, decimal_places=4)
    is_default: bool = False

    class Config:
        from_attributes = True

class AccountCreate(AccountBase):
    user_id: int

class AccountRead(AccountBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

class UpdateAccountDefault(BaseModel):
    is_default: bool = True

class UpdateAccountBalance(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=4)
    transaction_type: TransactionType

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v

class AccountResponse(BaseModel):
    message: str
    account: AccountRead