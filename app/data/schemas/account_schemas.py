from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

class AccountBase(BaseModel):
    type: str
    currency: str = "NGN"
    is_fundable: bool = True
    is_withdrawable: bool = True

class AccountCreate(AccountBase):
    user_id: int

class AccountUpdate(BaseModel):
    is_fundable: Optional[bool] = None
    is_withdrawable: Optional[bool] = None
    currency: Optional[str] = None

class VirtualAccountProfile(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=10, max_length=15)
    
    @validator('phone')
    def validate_phone(cls, v):
        if not v.replace('+', '').isdigit():
            raise ValueError('Phone number must contain only digits and optionally a + prefix')
        return v

class AccountCreateRequest(BaseModel):
    account_type: str = Field(..., description="Type of account to create")
    profile: VirtualAccountProfile

    @validator('account_type')
    def validate_account_type(cls, v):
        from app.data.models.account_models import AccountType
        if v not in AccountType.list():
            raise ValueError(f'Invalid account type. Must be one of: {", ".join(AccountType.list())}')
        return v

class VirtualAccountRead(BaseModel):
    id: int
    account_number: str
    account_name: str
    bank_name: str
    bank_code: str
    email: EmailStr
    phone: str
    reference: str
    
    class Config:
        from_attributes = True

class AccountRead(BaseModel):
    id: int
    user_id: int
    type: str
    key: str
    balance: Decimal = Field(default=0)
    currency: str
    is_fundable: bool
    is_withdrawable: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AccountResponse(BaseModel):
    message: str
    data: AccountRead

class VirtualAccountResponse(BaseModel):
    message: str
    data: VirtualAccountRead

class WebhookResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any]