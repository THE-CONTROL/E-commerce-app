from pydantic import BaseModel
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

FRONTEND_URL: str = os.getenv("FRONTEND_URL")
FRONTEND_RESET_PASSWORD_PATH: str = os.getenv("FRONTEND_RESET_PASSWORD_PATH")

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