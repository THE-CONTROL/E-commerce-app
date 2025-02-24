from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from sqlalchemy.orm import Session
from typing import List

from app.core.auth_dependency import get_current_user
from app.data.schemas.auth_schemas import ProtectedUser
from app.data.utils.database import get_db
from app.service.account_service import AccountService
from app.data.schemas.account_schemas import (
    VirtualAccountProfile,
    AccountRead,
    AccountResponse,
    VirtualAccountRead,
    WebhookResponse
)

class AccountRouter:
    def __init__(self):
        self.router = APIRouter(prefix="/accounts", tags=["accounts"])
        self._register_routes()

    def _register_routes(self):
        @self.router.post(
            "/",
            response_model=AccountResponse,
            status_code=status.HTTP_201_CREATED,
            description="Create a new account with virtual account"
        )
        async def create_account(
            profile: VirtualAccountProfile,
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user)
        ):
            """Create a new account with associated virtual account. Each user can only have one account."""
            try:
                result = await AccountService(session=db).create_account_with_virtual(
                    user_id=current_user.id,
                    profile_data=profile.model_dump()
                )
                return AccountResponse(
                    message="Account created successfully",
                    data=result["account"]
                )
            except HTTPException as e:
                raise e
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e)
                )
        
        @self.router.get(
            "/me",
            response_model=AccountRead,
            description="Get current user's account details"
        )
        async def get_my_account(
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user)
        ):
            """Get the current user's account details"""
            return AccountService(session=db).get_user_account(current_user.id)

        @self.router.get(
            "/me/virtual",
            response_model=VirtualAccountRead,
            description="Get current user's virtual account details"
        )
        async def get_my_virtual_account(
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user)
        ):
            """Get the current user's virtual account details"""
            return AccountService(session=db).get_virtual_account(current_user.id)

        @self.router.post(
            "/webhook/budpay",
            response_model=WebhookResponse,
            description="Handle Budpay webhook notifications"
        )
        async def handle_webhook(
            request: Request,
            db: Session = Depends(get_db),
            signature: str = Header(..., alias="X-Budpay-Signature")
        ):
            """Handle incoming webhook notifications from Budpay"""
            try:
                payload = await request.body()
                body = await request.json()
                
                return await AccountService(session=db).process_webhook(
                    signature=signature,
                    payload=payload,
                    body=body
                )
            except Exception as error:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(error)
                )

# Initialize router
account_router = AccountRouter().router