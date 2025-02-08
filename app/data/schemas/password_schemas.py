from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, StringConstraints, field_validator
from typing_extensions import Annotated

PasswordStr = Annotated[str, StringConstraints(min_length=8)]
PasscodeStr = Annotated[str, StringConstraints(min_length=4, max_length=4)]

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
    