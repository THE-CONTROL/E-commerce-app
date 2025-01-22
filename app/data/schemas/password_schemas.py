from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.data.schemas.user_schemas import UpdatePassword


class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    
class ResetPasswordToken(BaseModel):
    token: str
    expires_at: datetime
    user_id: int

class SetNewPassword(UpdatePassword):
    token: str
    
class PasswordResetResponse(BaseModel):
    message: str
    email: Optional[str] = None