from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.auth_handler import AuthHandler
from app.data.models.admin_models import AdminType
from app.data.schemas.auth_schemas import ProtectedUser
from app.data.utils.database import get_db
from app.service.user_service import UserService
from sqlalchemy.orm import Session


security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> ProtectedUser:
    """
    Dependency to get the current authenticated user
    """
    try:
        # Extract user_id from token
        user_id = AuthHandler.get_user_id_from_token(credentials.credentials)
        
        # Get user from database
        user = UserService(session=db).get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        return ProtectedUser(id=user.id, username=user.username)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
        
async def get_current_superadmin(
    current_user: ProtectedUser = Depends(get_current_user)
) -> ProtectedUser:
    if current_user.type != AdminType.SUPER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin privileges required"
        )
    return current_user