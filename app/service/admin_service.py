from typing import Dict, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.hash_helper import HashHelper
from app.data.schemas.password_schemas import UpdatePassword
from app.data.schemas.user_schemas import UserRead, UserResponse
from app.repository.account_repo import AccountRepository
from app.repository.admin_repo import AdminRepository
from app.service.base_service import BaseService
from app.data.models.admin_models import Admin, AdminType
from app.data.schemas.admin_schemas import AdminBase, AdminRead
from app.data.schemas.auth_schemas import UserCreate


class AdminService(BaseService[Admin, UserCreate, AdminBase]):
    def __init__(self, session: Session):
        super().__init__(repository=AdminRepository(session=session))
        self.account_repository = AccountRepository(session=session)
        self.session = session

    def deactivate_account(self, current_admin: int, admin_id: int) -> Dict:
        """Deactivate admin account"""
        if admin_id == current_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate your own account"
            )
        admin = self._repository.get_by_id(admin_id)  
        return self._repository.deactivate_account(admin)

    def activate_account(self, admin_id: int) -> Dict:
        """Activate admin account"""
        admin = self._repository.get_by_id(admin_id)  
        return self._repository.activate_account(admin)

    def update_type(self, admin_id: int, new_type: AdminType) -> Dict:
        """Update admin subscription type"""
        admin = self._repository.get_by_id(admin_id)
        return self._repository.update_type(admin, new_type)  

    def change_password(self, admin_id: int, password_data: UpdatePassword) -> Dict:
        """Change admin password"""
        admin = self._repository.get_by_id(admin_id)  
        
        if not self._repository.passwords_match(
            password_data.password,
            password_data.confirm_password
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match"
            )
            
        admin.password = HashHelper.get_password_hash(password_data.password)
        return self._repository.change_password(admin)
    
    def list_all_admins(self, skip: int = 0, limit: int = 100) -> List[AdminRead]:
        # Validate pagination parameters
        if skip < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Skip value cannot be negative"
            )
        if limit < 1:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Limit must be greater than 0"
            )
        if limit > 100:
            limit = 100  # Enforce maximum limit
                
        admins = self._repository.list_admins(skip=skip, limit=limit)
            
        # Convert to Pydantic models
        return [AdminRead.model_validate(admin) for admin in admins]
    
    def toggle_user_status(
        self,
        admin_id: int,
        user_id: int,
        activate: bool
    ) -> UserResponse:
        """
        Activate or deactivate a user's account.
        
        Args:
            admin_id: ID of the admin performing the action
            user_id: ID of the user to update
            activate: True to activate, False to deactivate
            
        Returns:
            UserResponse containing updated user data
        """
        try:
            # Get the user
            user = self.user_repository.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            # Check if status is already set
            if user.is_active == activate:
                action = "activated" if activate else "deactivated"
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User is already {action}"
                )

            # Update user status
            updated_user = self.user_repository.toggle_user_status(
                user=user,
                is_active=activate,
                admin_id=admin_id
            )

            # Prepare response message
            action = "activated" if activate else "deactivated"
            return UserResponse(
                message=f"User has been successfully {action}",
                user=UserRead.model_validate(updated_user)
            )

        except HTTPException as http_error:
            raise http_error
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating user status"
            )
            