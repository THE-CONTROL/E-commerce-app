from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    phone: str
    first_name: str
    last_name: str
    is_email_verified: bool = False
    is_phone_verified: bool = False
    is_suspended: bool = False

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
class UserRead(BaseModel):
    id: int
    username: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_email_verified: bool
    is_phone_verified: bool
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

    @property
    def full_name(self) -> str:
        """Returns the user's full name if both first and last names are present"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or ""