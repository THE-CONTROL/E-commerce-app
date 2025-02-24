# app/routes/account_routes.py
from fastapi import Depends, HTTPException, Header, Request, status
from sqlalchemy.orm import Session
from typing import List
from app.core.auth_dependency import get_current_user
from app.data.schemas.auth_schemas import ProtectedUser
from app.data.utils.database import get_db
from app.service.account_service import AccountService
from app.data.models.account_models import Account
from app.routes.base import BaseRouter
from app.data.schemas.account_schemas import (
    AccountCreateRequest,
    AccountUpdate,
    AccountRead,
    AccountResponse,
    VirtualAccountRead,
)

class AccountRouter(BaseRouter[Account, AccountCreateRequest, AccountUpdate, AccountService]):
    def __init__(self):
        super().__init__(
            service_class=AccountService,
            prefix="/accounts",
            tags=["accounts"],
            protected=True
        )
        self._register_account_routes()

    def _register_account_routes(self):
        @self.router.post(
            "/",
            response_model=AccountResponse,
            status_code=status.HTTP_201_CREATED
        )
        async def create_account(
            request: AccountCreateRequest,
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user)
        ):
            try:
                result = await self.service_class(session=db).create_account_with_virtual(
                    user_id=current_user.id,
                    account_type=request.account_type,
                    profile_data=request.profile.model_dump()
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
            "/list",
            response_model=List[AccountRead],
            summary="List Accounts"
        )
        async def list_accounts(
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user)
        ):
            try:
                return self.service_class(session=db).get_user_accounts(current_user.id)
            except Exception as error:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(error)
                )

        @self.router.get(
            "/{account_id}/details",
            response_model=AccountRead,
            summary="Get Account Details"
        )
        async def get_account_details(
            account_id: int,
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user)
        ):
            try:
                return self.service_class(session=db).get_account(
                    account_id=account_id,
                    user_id=current_user.id
                )
            except Exception as error:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(error)
                )

        @self.router.get(
            "/{account_id}/virtual",
            response_model=VirtualAccountRead,
            summary="Get Virtual Account"
        )
        async def get_virtual_account(
            account_id: int,
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user)
        ):
            try:
                return self.service_class(session=db).get_virtual_account(
                    account_id=account_id,
                    user_id=current_user.id
                )
            except Exception as error:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(error)
                )

        @self.router.post(
            "/webhook/budpay",
            summary="Budpay Webhook"
        )
        async def handle_webhook(
            request: Request,
            db: Session = Depends(get_db),
            signature: str = Header(..., alias="X-Budpay-Signature")
        ):
            try:
                payload = await request.body()
                body = await request.json()
                
                result = await self.service_class(session=db).process_webhook(
                    signature=signature,
                    payload=payload,
                    body=body
                )
                return result
            except Exception as error:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(error)
                )

# Initialize router
account_router = AccountRouter().router