import re


class ValidationMixin:
    """
    Mixin class for common validation methods
    """
    @staticmethod
    def validate_email(key: str, email: str) -> str:
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            raise ValueError(f"Invalid email format: {email}")
        return email

    @staticmethod
    def validate_age(key: str, age: int) -> int:
        if age < 18:
            raise ValueError("Age must be 18 or older")
        return age

    @staticmethod
    def passwords_match(password: str, confirm_password: str) -> bool:
        return password == confirm_password