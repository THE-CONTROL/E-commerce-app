from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Tuple, List
from datetime import datetime
from decimal import Decimal
from sqlalchemy import and_
from fastapi import HTTPException, status

from app.data.models.account_models import Account, VirtualBankAccount, AccountType

class AccountRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_with_virtual_account(
        self, 
        account_data: dict, 
        virtual_account_data: dict
    ) -> Tuple[Account, VirtualBankAccount]:
        """
        Create both main account and virtual account.
        Enforces one account per user rule.
        """
        try:
            # Check if user already has an account
            existing_account = self.get_user_account(account_data['user_id'])
            if existing_account:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already has an account"
                )

            # Use nested transaction for atomicity
            with self.session.begin_nested():
                # Create main account
                account = Account(**account_data)
                self.session.add(account)
                self.session.flush()
                
                # Add account_id to virtual account data
                virtual_account_data['account_id'] = account.id
                virtual_account_data['user_id'] = account_data['user_id']
                
                # Create virtual account
                virtual_account = VirtualBankAccount(**virtual_account_data)
                self.session.add(virtual_account)
                
            # Commit the transaction
            self.session.commit()
            return account, virtual_account
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )
        except Exception as e:
            self.session.rollback()
            raise e

    def get_user_account(self, user_id: int) -> Optional[Account]:
        """Get user's account - each user can only have one account"""
        return self.session.query(Account).filter(
            and_(
                Account.user_id == user_id,
                Account.type == AccountType.USER
            )
        ).first()

    def get_by_virtual_account(self, account_number: str) -> Optional[Account]:
        """Get main account by virtual account number"""
        virtual_account = self.session.query(VirtualBankAccount).filter(
            and_(
                VirtualBankAccount.account_number == account_number,
                VirtualBankAccount.is_active == True
            )
        ).first()
        
        if virtual_account:
            return self.session.query(Account).get(virtual_account.account_id)
        return None

    def credit_account(self, account: Account, amount: Decimal) -> Account:
        """Add money to account balance"""
        try:
            if not self.can_credit(account):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Account cannot be credited"
                )
                
            with self.session.begin_nested():
                account.balance += amount
                account.updated_at = datetime.utcnow()
                self.session.add(account)
                
            self.session.commit()
            return account
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )

    def debit_account(self, account: Account, amount: Decimal) -> Account:
        """Remove money from account balance"""
        try:
            if not self.can_debit(account, amount):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Account cannot be debited"
                )
                
            with self.session.begin_nested():
                account.balance -= amount
                account.updated_at = datetime.utcnow()
                self.session.add(account)
                
            self.session.commit()
            return account
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )

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