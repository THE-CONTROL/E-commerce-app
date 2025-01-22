import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from typing import List, Dict, Any, Optional
from pathlib import Path
import os
from app.core.email_config import EmailConfig

class EmailService:
    def __init__(self):
        # Create config from environment variables
        self.config = EmailConfig(
            MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
            MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
            MAIL_FROM=os.getenv("MAIL_USERNAME"),
            MAIL_PORT=int(os.getenv("MAIL_PORT")),
            MAIL_SERVER=os.getenv("MAIL_SERVER"),
            APP_NAME=os.getenv("APP_NAME"),
            TEMPLATE_FOLDER=os.getenv("TEMPLATE_FOLDER")
        )
        template_dir = Path(self.config.TEMPLATE_FOLDER)
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir)
        )

    async def send_email(
        self,
        subject: str,
        recipients: List[str],
        body: str,
        template_name: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Send an email"""
        try:
            # If template is provided, use it to render the body
            if template_name and template_data:
                template = self.jinja_env.get_template(template_name)
                body = template.render(**template_data)

            # Create message
            message = MIMEMultipart()
            message["From"] = f"{self.config.APP_NAME} <{self.config.MAIL_FROM}>"
            message["To"] = ", ".join(recipients)
            message["Subject"] = subject

            # Add body
            message.attach(MIMEText(body, "html"))

            # Create SMTP session
            with smtplib.SMTP(self.config.MAIL_SERVER, self.config.MAIL_PORT) as server:
                server.starttls()
                server.login(self.config.MAIL_USERNAME, self.config.MAIL_PASSWORD)
                server.send_message(message)

        except Exception as e:
            # Log error here
            raise Exception(f"Failed to send email: {str(e)}")

    async def send_password_reset_email(
        self,
        email: str,
        username: str,
        reset_link: str
    ) -> None:
        """Send password reset email"""
        subject = "Password Reset Request"
        template_data = {
            "username": username,
            "reset_link": reset_link,
            "app_name": self.config.APP_NAME,
            "support_email": self.config.MAIL_FROM
        }
        
        await self.send_email(
            subject=subject,
            recipients=[email],
            template_name="password_reset.html",
            template_data=template_data,
            body=""  # Will be overwritten by template
        )