from typing import Dict, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.repository.base_repo import BaseRepository
from app.data.models.account_models import Account, Currency
from app.data.schemas.account_schemas import (
    AccountCreate, TransactionType, UpdateAccountBalance
)

class AccountRepository(BaseRepository[Account, AccountCreate]):
    def __init__(self, session: Session):
        super().__init__(model=Account, session=session)
    
    def get_user_accounts(self, user_id: int) -> List[Account]:
        """Get all accounts for a user"""
        return self.session.query(self.model).filter(self.model.user_id == user_id).all()

    def get_account_by_number(self, account_number: str) -> Optional[Account]:
        """Get account by account number"""
        return self.get_by_field("account_number", account_number)

    def get_user_account_by_currency(self, user_id: int, currency: Currency) -> Optional[Account]:
        """Get user's account by currency"""
        return self.session.query(self.model).filter(
            and_(
                self.model.user_id == user_id,
                self.model.currency == currency
            )
        ).first()

    def create_user_accounts(self, user_id: int) -> List[Dict]:
        """Create accounts for all supported currencies"""
        accounts = []
        try:
            for currency in Currency:
                account_data = AccountCreate(
                    user_id=user_id,
                    account_number=self._generate_account_number(),
                    currency=currency,
                    is_default=currency == Currency.NGN
                )
                result = self.create(account_data.model_dump())
                accounts.append({**account_data.model_dump(), "id": result["id"]})
        except Exception as e:
            self.session.rollback()
            raise e
        return accounts

    def update_balance(self, account: Account, update_data: UpdateAccountBalance) -> Dict:
        """Update account balance based on transaction type"""
        try:
            # Calculate new balance based on transaction type
            if update_data.transaction_type == TransactionType.CREDIT:
                new_balance = account.balance + update_data.amount
            else:  # DEBIT
                new_balance = account.balance - update_data.amount
                
                # Check for sufficient funds
                if new_balance < 0:
                    raise ValueError(
                        f"Insufficient funds. Current balance: {account.balance}, "
                        f"Attempted debit: {update_data.amount}"
                    )
            
            # Update account
            account.balance = new_balance
            account.updated_at = datetime.now(timezone.utc)
            return self.update(account)
            
        except Exception as e:
            self.session.rollback()
            raise e

    def set_account_default(self, account: Account, is_default: bool = True) -> Dict:
        """Set account as default for its currency"""
        try:
            # Begin transaction
            self.session.begin_nested()
            
            # If setting as default, unset other accounts of same currency
            if is_default:
                other_accounts = self.session.query(self.model).filter(
                    and_(
                        self.model.user_id == account.user_id,
                        self.model.currency == account.currency,
                        self.model.id != account.id
                    )
                ).all()
                
                for other_account in other_accounts:
                    other_account.is_default = False
                    self.session.add(other_account)

            # Update target account
            account.is_default = is_default
            account.updated_at = datetime.now(timezone.utc)
            result = self.update(account)
            
            # Commit transaction
            self.session.commit()
            return result
            
        except Exception as e:
            self.session.rollback()
            raise e

    def activate_account(self, account: Account) -> Dict:
        """Activate an account"""
        account.is_active = True
        account.updated_at = datetime.now(timezone.utc)
        return self.update(account)

    def deactivate_account(self, account: Account) -> Dict:
        """Deactivate an account"""
        account.is_active = False
        account.updated_at = datetime.now(timezone.utc)
        return self.update(account)

    def _generate_account_number(self) -> str:
        """Generate a unique account number"""
        import random
        while True:
            account_number = str(random.randint(1000000000, 9999999999))
            existing = self.get_by_field("account_number", account_number)
            if not existing:
                return account_number