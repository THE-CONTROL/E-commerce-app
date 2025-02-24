# app/data/schemas/account_schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

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
    

class VirtualAccountBase(BaseModel):
    email: EmailStr
    phone: str
    first_name: str
    last_name: str

class VirtualAccountCreate(VirtualAccountBase):
    pass

class VirtualAccountRead(BaseModel):
    id: int
    account_number: str
    account_name: str
    bank_name: str
    bank_code: str
    email: str
    phone: str
    reference: str
    
    class Config:
        from_attributes = True
        
        
class VirtualAccountResponse(BaseModel):
    message: str
    data: VirtualAccountRead
    
class VirtualAccountProfile(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone: str

class AccountCreateRequest(BaseModel):
    account_type: str
    profile: VirtualAccountProfile

class AccountRead(BaseModel):
    id: int
    user_id: int
    type: str
    key: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AccountResponse(BaseModel):
    message: str
    data: AccountRead