from pydantic import BaseModel
from functools import lru_cache
import os
from dotenv import load_dotenv
import pyotp

load_dotenv()

FRONTEND_URL: str = os.getenv("FRONTEND_URL")
FRONTEND_RESET_PASSWORD_PATH: str = os.getenv("FRONTEND_RESET_PASSWORD_PATH")

OTP_KEY = os.getenv("PYOTP_KEY")
TOTP = pyotp.TOTP(OTP_KEY)

BUDPAY_SECRET_KEY=os.getenv("BUDPAY_SECRET_KEY")
API_BASE_URL=os.getenv("API_BASE_URL")
SYSTEM_FEE_ACCOUNT_ID=os.getenv("SYSTEM_FEE_ACCOUNT_ID")

class Settings(BaseModel):
    # Frontend URL Settings
    def get_password_reset_link(self, token: str) -> str:
        """Generate password reset link with token"""
        return f"{FRONTEND_URL.rstrip('/')}{FRONTEND_RESET_PASSWORD_PATH}?token={token}"

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings(
        FRONTEND_URL=FRONTEND_URL,
        FRONTEND_RESET_PASSWORD_PATH=FRONTEND_RESET_PASSWORD_PATH
    )