from pydantic import BaseModel, EmailStr, StringConstraints, Field, field_validator
from typing import Optional, List
from typing_extensions import Annotated
from datetime import datetime
from app.data.models.user_models import UserTier
from app.data.schemas.account_schemas import AccountRead

# Custom string types with constraints
UsernameStr = Annotated[str, StringConstraints(min_length=3, max_length=50)]
NINStr = Annotated[str, StringConstraints(min_length=11, max_length=11)]
BVNStr = Annotated[str, StringConstraints(min_length=11, max_length=11)]
PasswordStr = Annotated[str, StringConstraints(min_length=8)]

# Password schemas
class UpdatePassword(BaseModel):
    password: PasswordStr
    confirm_password: PasswordStr

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if v != info.data.get("password"):
            raise ValueError("Passwords do not match")
        return v

# User schemas
class UserBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[UsernameStr] = None
    age: Optional[int] = Field(None, ge=18)
    address: Optional[str] = None
    email: Optional[EmailStr] = None
    nin: Optional[NINStr] = None
    bvn: Optional[BVNStr] = None
    
    @field_validator("age")
    @classmethod
    def validate_age(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 18:
            raise ValueError("User must be 18 or older")
        return v

    class Config:
        from_attributes = True

class UserRead(UserBase):
    id: int
    tier: Optional[UserTier] = None
    verified: bool = False
    is_active: bool = True
    date_joined: datetime
    last_login: Optional[datetime] = None
    updated_at: datetime
    accounts: List[AccountRead] = []

class UpdateUserTier(BaseModel):
    tier: UserTier

class UserResponse(BaseModel):
    message: str
    user: UserRead