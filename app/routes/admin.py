from fastapi import Depends, HTTPException, status
from typing import List, Optional
from app.data.models.user_models import UserTier
from app.data.schemas.admin_schemas import AdminBase, AdminRead, AdminResponse
from app.data.schemas.auth_schemas import ProtectedUser
from app.data.schemas.user_schemas import UserRead, UserResponse
from app.data.utils.database import get_db
from app.core.auth_dependency import get_current_user, get_current_superadmin
from app.data.models.admin_models import Admin, AdminType
from app.routes.base import BaseRouter
from app.service.admin_service import AdminService
from sqlalchemy.orm import Session
from app.core.logging import logger


class AdminRouter(BaseRouter[Admin, AdminBase, AdminBase, AdminService]):
    def __init__(self):
        super().__init__(
            service_class=AdminService,
            prefix="/admins",
            tags=["admins"],
            protected=True
        )
        self._register_admin_routes()

    def _register_admin_routes(self):
        @self.router.get(
            "/me",
            response_model=AdminRead,
        )
        async def get_current_admin_info(
            db: Session = Depends(get_db),
            current_admin: ProtectedUser = Depends(get_current_user)
        ):
            try:
                admin = self.service_class(session=db).get_by_id(id=current_admin.id)
            except Exception as error:
                raise error

        @self.router.put(
            "/me",
            response_model=AdminResponse,
        )
        async def update_current_admin(
            update_data: AdminBase,
            db: Session = Depends(get_db),
            current_admin: ProtectedUser = Depends(get_current_user)
        ):
            try:
                return self.service_class(session=db).update(
                    id=current_admin.id,
                    data=update_data
                )
            except Exception as error:
                logger.error(f"Error updating admin: {str(error)}")
                raise error

        @self.router.put(
            "/type/{admin_type}",
            response_model=AdminResponse,
        )
        async def update_admin_type(
            new_type: AdminType,
            admin_id: int,
            db: Session = Depends(get_db),
            current_admin: ProtectedUser = Depends(get_current_superadmin)
        ):
            try:
                updated_admin = self.service_class(session=db).update_type(admin_id,new_type)
                return AdminResponse(
                    message="Admin type updated successfully",
                    user=updated_admin
                )
            except Exception as error:
                logger.error(f"Error updating admin type: {str(error)}")
                raise error

        @self.router.put(
            "/{admin_id}/deactivate",
            response_model=AdminResponse,
        )
        async def deactivate_admin_account(
            admin_id: int,
            db: Session = Depends(get_db),
            current_admin: ProtectedUser = Depends(get_current_superadmin)
        ):  
            try:
                deactivated_admin = self.service_class(session=db).deactivate_account(current_admin.id, admin_id)
                return AdminResponse(
                    message="Admin account deactivated successfully",
                    user=deactivated_admin
                )
            except Exception as error:
                logger.error(f"Error deactivating admin account: {str(error)}")
                raise error

        @self.router.get("/", response_model=List[AdminRead])
        async def list_admins(
            skip: int = 0,
            limit: int = 100,
            db: Session = Depends(get_db),
            current_admin: ProtectedUser = Depends(get_current_superadmin)
        ):
            try:
                return self.service_class(session=db).list_all_admins(skip=skip, limit=limit)
            except HTTPException as http_error:
                raise http_error
            except Exception as error:
                logger.error(f"Error deactivating admin account: {str(error)}")
                raise error

        @self.router.get("/users", response_model=List[UserRead],)
        async def list_users(
            skip: int = 0,
            limit: int = 100,
            tier: Optional[UserTier] = None,
            verified: Optional[bool] = None,
            is_active: Optional[bool] = None,
            min_age: Optional[int] = None,
            max_age: Optional[int] = None,
            search: Optional[str] = None,
            db: Session = Depends(get_db),
            current_admin: ProtectedUser = Depends(get_current_user)
        ):
            """
            List users with various filter options.
            """
            try:
                filters = {}
                
                if tier:
                    filters['tier'] = tier
                if verified is not None:
                    filters['verified'] = verified
                if is_active is not None:
                    filters['is_active'] = is_active
                if min_age is not None and max_age is not None:
                    filters['age_range'] = (min_age, max_age)
                    
                return self.service_class(session=db).list_filtered_users(
                    skip=skip,
                    limit=limit,
                    filters=filters,
                    search_term=search
                )
                
            except HTTPException as http_error:
                raise http_error
            except Exception as error:
                logger.error(f"Error listing users: {str(error)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error"
                )

        @self.router.get(
            "/users/advanced-filter",
            response_model=List[UserRead],
        )
        async def filter_users(
            skip: int = 0,
            limit: int = 100,
            nin: Optional[str] = None,
            bvn: Optional[str] = None,
            email: Optional[str] = None,
            username: Optional[str] = None,
            db: Session = Depends(get_db),
            current_admin: ProtectedUser = Depends(get_current_user)
        ):
            """
            Advanced filter for users including Nigerian-specific fields.
            """
            try:
                filters = {}
                
                for field, value in {
                    'nin': nin,
                    'bvn': bvn,
                    'email': email,
                    'username': username
                }.items():
                    if value:
                        filters[field] = value
                        
                return self.service_class(session=db).list_filtered_users(
                    skip=skip,
                    limit=limit,
                    filters=filters
                )
                
            except HTTPException as http_error:
                raise http_error
            except Exception as error:
                logger.error(f"Error filtering users: {str(error)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error"
                )
                
        @self.router.put(
            "/users/{user_id}/deactivate",
            response_model=UserResponse,
            summary="Deactivate user",
            description="Admin deactivates a user account"
        )
        async def admin_deactivate_user(
            user_id: int,
            db: Session = Depends(get_db),
            current_admin: ProtectedUser = Depends(get_current_user)
        ):
            """
            Deactivate a user account as an admin.
            
            Args:
                user_id: ID of the user to deactivate
                
            Returns:
                UserResponse containing updated user data
            """
            try:
                admin_service = self.service_class(session=db)
                return admin_service.toggle_user_status(
                    admin_id=current_admin.id,
                    user_id=user_id,
                    activate=False
                )
            except HTTPException as http_error:
                raise http_error
            except Exception as error:
                logger.error(f"Error in admin_deactivate_user: {str(error)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error"
                )

        @self.router.put(
            "/users/{user_id}/activate",
            response_model=UserResponse,
            summary="Activate user",
            description="Admin activates a user account"
        )
        async def admin_activate_user(
            user_id: int,
            db: Session = Depends(get_db),
            current_admin: ProtectedUser = Depends(get_current_user)
        ):
            """
            Activate a user account as an admin.
            
            Args:
                user_id: ID of the user to activate
                
            Returns:
                UserResponse containing updated user data
            """
            try:
                admin_service = self.service_class(session=db)
                return admin_service.toggle_user_status(
                    admin_id=current_admin.id,
                    user_id=user_id,
                    activate=True
                )
            except HTTPException as http_error:
                raise http_error
            except Exception as error:
                logger.error(f"Error in admin_activate_user: {str(error)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error"
                )

# Initialize router
admin_router = AdminRouter().router