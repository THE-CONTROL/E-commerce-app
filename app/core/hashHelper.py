from bcrypt import checkpw, hashpw, gensalt
from typing import Optional
from fastapi import HTTPException, status

class HashConfig:
    # Default number of rounds for bcrypt
    ROUNDS = 12  # Industry standard, adjust based on your security needs

class HashHelper:
    """
    Helper class for password hashing and verification
    """
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password
        
        Args:
            plain_password: The password in plain text
            hashed_password: The hashed password to compare against
            
        Returns:
            bool: True if passwords match, False otherwise
            
        Raises:
            HTTPException: If there's an encoding error or invalid hash format
        """
        try:
            return checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8")
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid password format"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password verification failed"
            )
    
    @staticmethod
    def get_password_hash(plain_password: str, rounds: Optional[int] = None) -> str:
        """
        Hash a password using bcrypt
        
        Args:
            plain_password: The password to hash
            rounds: Optional number of rounds for bcrypt (defaults to HashConfig.ROUNDS)
            
        Returns:
            str: The hashed password
            
        Raises:
            HTTPException: If there's an encoding error or hashing fails
        """
        try:
            salt = gensalt(rounds or HashConfig.ROUNDS)
            return hashpw(
                plain_password.encode("utf-8"),
                salt
            ).decode("utf-8")
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid password format"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password hashing failed"
            )

    @staticmethod
    def validate_password_strength(password: str, 
                                 min_length: int = 8,
                                 require_upper: bool = True,
                                 require_lower: bool = True,
                                 require_digit: bool = True,
                                 require_special: bool = True) -> bool:
        """
        Validate password strength based on configurable criteria
        
        Args:
            password: The password to validate
            min_length: Minimum required length
            require_upper: Require uppercase letters
            require_lower: Require lowercase letters
            require_digit: Require digits
            require_special: Require special characters
            
        Returns:
            bool: True if password meets all criteria, False otherwise
        """
        if len(password) < min_length:
            return False
            
        if require_upper and not any(c.isupper() for c in password):
            return False
            
        if require_lower and not any(c.islower() for c in password):
            return False
            
        if require_digit and not any(c.isdigit() for c in password):
            return False
            
        if require_special and not any(not c.isalnum() for c in password):
            return False
            
        return True

    @classmethod
    def hash_and_validate(cls, 
                         password: str,
                         validate_strength: bool = True,
                         **validation_options) -> str:
        """
        Validate password strength and hash it in one step
        
        Args:
            password: The password to validate and hash
            validate_strength: Whether to validate password strength
            **validation_options: Options to pass to validate_password_strength
            
        Returns:
            str: The hashed password
            
        Raises:
            HTTPException: If password is too weak or hashing fails
        """
        if validate_strength and not cls.validate_password_strength(
            password, **validation_options
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password too weak. Must contain uppercase, lowercase, "
                      "digits, special characters, and be at least 8 characters long."
            )
            
        return cls.get_password_hash(password)