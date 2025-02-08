from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.data.models.admin_models import AdminType
from app.data.schemas.user_schemas import UsernameStr


class AdminBase(BaseModel):
    username: Optional[UsernameStr] = None
    email: Optional[EmailStr] = None
    
    class Config:
        from_attributes = True  # Updated from orm_mode to from_attributes


class AdminRead(AdminBase):
    id: int
    type: Optional[AdminType] = None
    is_active: bool = True
    date_joined: datetime
    last_login: Optional[datetime] = None
    updated_at: datetime


class AdminResponse(BaseModel):
    message: str
    user: AdminRead