from bcrypt import checkpw, hashpw, gensalt
from typing import Literal
from fastapi import HTTPException, status

class HashConfig:
    # Default number of rounds for bcrypt
    PASSWORD_ROUNDS = 12  # Industry standard for passwords
    PASSCODE_ROUNDS = 8   # Slightly lower for passcodes due to limited complexity

class HashHelper:
    """
    Helper class for password and passcode hashing and verification
    """
    
    @staticmethod
    def verify_credential(plain_text: str, hashed_text: str) -> bool:
        """
        Verify a plain password or passcode against a hashed value
        
        Args:
            plain_text: The password/passcode in plain text
            hashed_text: The hashed value to compare against
            
        Returns:
            bool: True if credentials match, False otherwise
            
        Raises:
            HTTPException: If there's an encoding error or invalid hash format
        """
        try:
            return checkpw(
                plain_text.encode("utf-8"),
                hashed_text.encode("utf-8")
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid credential format"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Credential verification failed"
            )
    
    @staticmethod
    def get_hash(plain_text: str, credential_type: Literal["password", "passcode"]) -> str:
        """
        Hash a password or passcode using bcrypt
        
        Args:
            plain_text: The text to hash
            credential_type: Either "password" or "passcode"
            
        Returns:
            str: The hashed value
            
        Raises:
            HTTPException: If there's an encoding error or hashing fails
        """
        try:
            rounds = (HashConfig.PASSWORD_ROUNDS if credential_type == "password" 
                     else HashConfig.PASSCODE_ROUNDS)
            salt = gensalt(rounds)
            return hashpw(
                plain_text.encode("utf-8"),
                salt
            ).decode("utf-8")
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid {credential_type} format"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{credential_type.capitalize()} hashing failed"
            )

    @staticmethod
    def validate_password(password: str, 
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

    @staticmethod
    def validate_passcode(passcode: str, length: int = 4) -> bool:
        """
        Validate a numeric passcode
        
        Args:
            passcode: The passcode to validate
            length: Required length of the passcode (default 4)
            
        Returns:
            bool: True if passcode is valid, False otherwise
        """
        return len(passcode) == length and passcode.isdigit()

    @classmethod
    def hash_and_validate(cls, 
                         text: str,
                         credential_type: Literal["password", "passcode"],
                         validate: bool = True,
                         **validation_options) -> str:
        """
        Validate and hash a password or passcode in one step
        
        Args:
            text: The password or passcode to validate and hash
            credential_type: Either "password" or "passcode"
            validate: Whether to validate before hashing
            **validation_options: Options to pass to respective validation method
            
        Returns:
            str: The hashed value
            
        Raises:
            HTTPException: If validation fails or hashing fails
        """
        if validate:
            if credential_type == "password":
                if not cls.validate_password(text, **validation_options):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Password too weak. Must contain uppercase, lowercase, "
                              "digits, special characters, and be at least 8 characters long."
                    )
            else:  # passcode
                if not cls.validate_passcode(text, **validation_options):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid passcode. Must be exactly "
                              f"{validation_options.get('length', 4)} digits."
                    )
            
        return cls.get_hash(text, credential_type)