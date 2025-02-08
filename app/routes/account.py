from fastapi import APIRouter, Depends, Path
from typing import List
from sqlalchemy.orm import Session
from app.core.auth_dependency import get_current_user
from app.data.schemas.auth_schemas import ProtectedUser
from app.data.utils.database import get_db
from app.service.account_service import AccountService
from app.data.schemas.account_schemas import (
    AccountRead, AccountResponse, UpdateAccountBalance
)
 
class AccountRouter:
    def __init__(self):
        self.router = APIRouter(prefix="/accounts", tags=["accounts"])
        self._register_account_routes()

    def _register_account_routes(self):
        @self.router.get("/", response_model=List[AccountRead])
        async def get_user_accounts(
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user)
        ):
            """Get all accounts for the authenticated user"""
            return AccountService(session=db).get_user_accounts(current_user.id)

        @self.router.get("/{account_number}", response_model=AccountRead)
        async def get_single_account(
            account_number: str = Path(..., min_length=10, max_length=10),
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user)
        ):
            """Get details of a single account"""
            return AccountService(session=db).get_account_by_number(
                account_number=account_number,
                user_id=current_user.id
            )

        @self.router.patch("/{account_number}/balance", response_model=AccountResponse)
        async def update_balance(
            update_data: UpdateAccountBalance,
            account_number: str = Path(..., min_length=10, max_length=10),
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user)
        ):
            """Update account balance with credit/debit transaction"""
            return AccountService(session=db).update_balance(account_number, update_data)
    

# Initialize router
account_router = AccountRouter().router