from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from app.data.models.admin_models import AdminType
from app.data.schemas.password_schemas import UpdatePassword


# Auth schemas
class UserCreate(UpdatePassword):
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    
class AdminCreate(UpdatePassword):
    username: str
    email: Optional[EmailStr] = None
    type: Optional[AdminType] = None
    
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
