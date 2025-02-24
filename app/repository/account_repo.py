# app/repository/account_repo.py
from sqlalchemy.orm import Session
from typing import Optional, Tuple
from datetime import datetime
from decimal import Decimal
from sqlalchemy import and_
from app.data.models.account_models import Account, VirtualBankAccount, AccountType

class AccountRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_with_virtual_account(
        self, 
        account_data: dict, 
        virtual_account_data: dict
    ) -> Tuple[Account, VirtualBankAccount]:
        """Create both main account and virtual account"""
        try:
            self.session.begin_nested()
            
            # Create main account
            account = Account(**account_data)
            self.session.add(account)
            self.session.flush()  # Get the account ID
            
            # Add account_id to virtual account data
            virtual_account_data['account_id'] = account.id
            virtual_account_data['user_id'] = account_data['user_id']
            
            # Create virtual account
            virtual_account = VirtualBankAccount(**virtual_account_data)
            self.session.add(virtual_account)
            
            self.session.commit()
            return account, virtual_account
            
        except Exception as e:
            self.session.rollback()
            raise e

    def get_user_account(self, user_id: int) -> Optional[Account]:
        """Get user's primary account"""
        return self.session.query(Account).filter(
            Account.user_id == user_id,
            Account.type == 'user'
        ).first()

    def get_by_id(self, account_id: int) -> Optional[Account]:
        """Get account by ID"""
        return self.session.query(Account).get(account_id)

    def get_by_type(self, account_type: AccountType) -> Optional[Account]:
        """Get account by type"""
        return self.session.query(Account).filter(
            Account.type == account_type
        ).first()

    def get_virtual_account(self, account_id: int) -> Optional[VirtualBankAccount]:
        """Get active virtual account for main account"""
        return self.session.query(VirtualBankAccount).filter(
            and_(
                VirtualBankAccount.account_id == account_id,
                VirtualBankAccount.is_active == True
            )
        ).first()

    def get_by_virtual_account(self, account_number: str) -> Optional[Account]:
        """Get main account by virtual account number"""
        virtual_account = self.session.query(VirtualBankAccount).filter(
            VirtualBankAccount.account_number == account_number
        ).first()
        
        if virtual_account:
            return self.session.query(Account).get(virtual_account.account_id)
        return None

    def credit_account(self, account: Account, amount: Decimal) -> Account:
        """Add money to account balance"""
        try:
            if not self.can_credit(account):
                raise ValueError("Account cannot be credited")
            account.balance += amount
            account.updated_at = datetime.utcnow()
            self.session.add(account)
            return account
        except Exception as e:
            raise e

    def debit_account(self, account: Account, amount: Decimal) -> Account:
        """Remove money from account balance"""
        try:
            if not self.can_debit(account, amount):
                raise ValueError("Account cannot be debited")
            account.balance -= amount
            account.updated_at = datetime.utcnow()
            self.session.add(account)
            return account
        except Exception as e:
            raise e

    def can_debit(self, account: Account, amount: Decimal) -> bool:
        """Check if account can be debited"""
        return (
            not account.locked 
            and not account.is_suspended 
            and account.is_withdrawable 
            and account.balance >= amount
        )

    def can_credit(self, account: Account) -> bool:
        """Check if account can be credited"""
        return (
            not account.locked 
            and not account.is_suspended 
            and account.is_fundable
        )
