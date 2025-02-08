from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from app.data.models.admin_models import AdminType
from app.data.schemas.password_schemas import UpdatePassword
from app.data.schemas.user_schemas import UsernameStr, NINStr, BVNStr


# Auth schemas
class UserCreate(UpdatePassword):
    username: UsernameStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(None, ge=18)
    address: Optional[str] = None
    nin: Optional[NINStr] = None
    bvn: Optional[BVNStr] = None

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 18:
            raise ValueError("User must be 18 or older")
        return v
    
class AdminCreate(UpdatePassword):
    username: UsernameStr
    email: Optional[EmailStr] = None
    type: Optional[AdminType] = None

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 18:
            raise ValueError("User must be 18 or older")
        return v
    
class UserLogin(BaseModel):
    username: str
    password: str

class ProtectedUser(BaseModel):
    id: int
    username: str
    
class RefreshRequest(BaseModel):
    refresh_token: str
    
class RefreshResponse(BaseModel):
    access_token: str
    
class UserWithToken(RefreshResponse):
    refresh_token: str
    token_type: str = "bearer"

class TokenResponse(BaseModel):
    message: str
    token: UserWithToken
