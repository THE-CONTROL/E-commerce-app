from pydantic import BaseModel

class EmailConfig(BaseModel):
    """Email configuration"""
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    APP_NAME: str = "Your App Name"
    TEMPLATE_FOLDER: str = "app/templates"