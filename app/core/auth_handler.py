from typing import Optional, Dict, Any
import time
import jwt
from dotenv import load_dotenv
import os
from fastapi import HTTPException, status

# Load environment variables
load_dotenv()

class AuthConfig:
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # 15 minutes
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30    # 30 days

    @classmethod
    def validate_config(cls) -> None:
        if not cls.JWT_SECRET or not cls.JWT_ALGORITHM:
            raise ValueError("JWT_SECRET and JWT_ALGORITHM must be set in environment variables")

class AuthHandler:
    @staticmethod
    def _create_token(payload: Dict[str, Any], expires_delta: int) -> str:
        """
        Create a JWT token with given payload and expiration time
        """
        to_encode = payload.copy()
        to_encode.update({
            "expires": time.time() + expires_delta
        })
        
        try:
            return jwt.encode(
                to_encode,
                AuthConfig.JWT_SECRET,
                algorithm=AuthConfig.JWT_ALGORITHM
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create token"
            )

    @classmethod
    def sign_jwt(cls, user_id: int) -> Dict[str, str]:
        """
        Create both access and refresh tokens for a user
        """
        # Validate configuration
        AuthConfig.validate_config()
        
        try:
            # Create access token
            access_token = cls._create_token(
                payload={"user_id": user_id},
                expires_delta=AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
            
            # Create refresh token
            refresh_token = cls._create_token(
                payload={"user_id": user_id},
                expires_delta=AuthConfig.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
            )
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token generation failed"
            )
        
    @classmethod
    def decode_jwt(cls, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode and validate a JWT token
        """
        try:
            decoded_token = jwt.decode(
                token,
                AuthConfig.JWT_SECRET,
                algorithms=[AuthConfig.JWT_ALGORITHM]
            )
            
            # Check if token has expired
            if decoded_token["expires"] >= time.time():
                return decoded_token
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token validation failed"
            )
        
    @classmethod
    def refresh_jwt(cls, refresh_token: str) -> str:
        """
        Create a new access token using a refresh token
        """
        try:
            # Decode and validate refresh token
            decoded_token = cls.decode_jwt(refresh_token)
            if not decoded_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            # Create new access token
            user_id = decoded_token.get("user_id")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
                
            return cls._create_token(
                payload={"user_id": user_id},
                expires_delta=AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token refresh failed"
            )

    @classmethod
    def get_user_id_from_token(cls, token: str) -> int:
        """
        Extract user_id from a token
        """
        decoded = cls.decode_jwt(token)
        if not decoded or "user_id" not in decoded:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        return decoded["user_id"]