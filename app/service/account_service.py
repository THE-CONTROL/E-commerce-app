from fastapi import HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from app.service.base_service import BaseService
from app.data.models.account_models import Account, Currency
from app.data.schemas.account_schemas import (
    AccountCreate, AccountRead, AccountResponse,
    UpdateAccountBalance
)
from app.repository.account_repo import AccountRepository


class AccountService(BaseService[Account, AccountCreate, AccountRead]):
    def __init__(self, session: Session):
        super().__init__(repository=AccountRepository(session=session))
        self._repository: AccountRepository = self._repository

    def get_user_accounts(self, user_id: int) -> List[AccountRead]:
        """Get all accounts for a user"""
        accounts = self._repository.get_user_accounts(user_id)
        return [AccountRead.model_validate(account) for account in accounts]

    def get_account_by_number(self, account_number: str, user_id: int) -> AccountRead:
        """Get account by account number"""
        account = self._repository.get_account_by_number(account_number)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
            
        # Verify account ownership
        if account.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this account is forbidden"
            )
        return AccountRead.model_validate(account)

    def get_user_account_by_currency(self, user_id: int, currency: Currency) -> AccountRead:
        """Get user's account by currency"""
        account = self._repository.get_user_account_by_currency(user_id, currency)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        return AccountRead.model_validate(account)

    def update_balance(
        self, account_number: str, update_data: UpdateAccountBalance
    ) -> AccountResponse:
        """Update account balance based on transaction type"""
        account = self._repository.get_account_by_number(account_number)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        if not account.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update balance of inactive account"
            )

        try:
            result = self._repository.update_balance(account, update_data)
            return AccountResponse(
                message=f"Successfully processed {update_data.transaction_type} transaction",
                account=AccountRead.model_validate(result)
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
