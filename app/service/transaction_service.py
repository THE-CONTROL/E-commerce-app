# app/service/transaction_service.py
from typing import Dict, Optional
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repository.account_repo import AccountRepository
from app.repository.transaction_repo import TransactionRepository
from app.service.budpay_service import BudpayService
from app.data.models.transaction_models import TransactionType, TransactionStatus
from datetime import datetime

class TransactionService:
    def __init__(self, session: Session):
        self.session = session
        self.transaction_repo = TransactionRepository(session)
        self.account_repo = AccountRepository(session)
        self.budpay_service = BudpayService()

    async def process_product_payment(
        self,
        buyer_account_id: int,
        store_account_id: int,
        product_id: int,
        amount: Decimal
    ) -> Dict:
        """Process product purchase payment with virtual accounts"""
        try:
            self.session.begin_nested()
            
            # Get accounts and virtual accounts
            buyer_account = self.account_repo.get_by_id(buyer_account_id)
            store_account = self.account_repo.get_by_id(store_account_id)
            app_account = self.account_repo.get_by_type("platform")
            
            buyer_virtual = self.account_repo.get_virtual_account(buyer_account_id)
            store_virtual = self.account_repo.get_virtual_account(store_account_id)
            app_virtual = self.account_repo.get_virtual_account(app_account.id)
            
            if not all([buyer_account, store_account, app_account, 
                       buyer_virtual, store_virtual, app_virtual]):
                raise ValueError("Invalid account configuration")
            
            # Calculate fee (1.5%)
            fee = (amount * Decimal('0.015')).quantize(Decimal('0.01'))
            store_amount = amount - fee
            
            # Verify buyer has sufficient balance
            buyer_balance = await self.budpay_service.get_virtual_account_balance(
                buyer_virtual.account_number
            )
            if Decimal(str(buyer_balance["balance"])) < amount:
                raise ValueError("Insufficient funds")
            
            # Create transactions in PENDING state
            debit_txn = self.transaction_repo.create_transaction({
                "type": TransactionType.PRODUCT_PAYMENT,
                "amount": amount,
                "description": f"Payment for product {product_id}",
                "status": TransactionStatus.PENDING,
                "account_id": buyer_account_id
            })
            
            credit_txn = self.transaction_repo.create_transaction({
                "type": TransactionType.PRODUCT_PAYMENT,
                "amount": store_amount,
                "fee_amount": fee,
                "description": f"Payment received for product {product_id}",
                "status": TransactionStatus.PENDING,
                "account_id": store_account_id,
                "reference": debit_txn.reference
            })
            
            fee_txn = self.transaction_repo.create_transaction({
                "type": TransactionType.FEE,
                "amount": fee,
                "description": f"Fee for product {product_id}",
                "status": TransactionStatus.PENDING,
                "account_id": app_account.id,
                "reference": debit_txn.reference
            })
            
            try:
                # Transfer amount to store's virtual account
                await self.budpay_service.transfer_to_virtual_account(
                    from_account=buyer_virtual.account_number,
                    to_account=store_virtual.account_number,
                    amount=store_amount,
                    description=f"Payment for product {product_id}"
                )
                
                # Transfer fee to platform's virtual account
                await self.budpay_service.transfer_to_virtual_account(
                    from_account=buyer_virtual.account_number,
                    to_account=app_virtual.account_number,
                    amount=fee,
                    description=f"Platform fee for product {product_id}"
                )
                
                # Update account balances
                self.account_repo.debit_account(buyer_account, amount)
                self.account_repo.credit_account(store_account, store_amount)
                self.account_repo.credit_account(app_account, fee)
                
                # Update transaction statuses
                for txn in [debit_txn, credit_txn, fee_txn]:
                    self.transaction_repo.update_status(
                        txn, 
                        TransactionStatus.COMPLETED,
                        commit=False
                    )
                
                self.session.commit()
                
                return {
                    "status": "success",
                    "message": "Payment processed successfully",
                    "data": {
                        "buyer_transaction": debit_txn,
                        "store_transaction": credit_txn,
                        "fee_transaction": fee_txn,
                        "amount": amount,
                        "store_amount": store_amount,
                        "fee": fee
                    }
                }
                
            except Exception as e:
                self.session.rollback()
                
                # Update transaction statuses to FAILED
                for txn in [debit_txn, credit_txn, fee_txn]:
                    self.transaction_repo.update_status(
                        txn,
                        TransactionStatus.FAILED,
                        commit=True
                    )
                
                raise e
            
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

    async def process_subscription_payment(
        self,
        user_account_id: int,
        store_id: int,
        amount: Decimal
    ) -> Dict:
        """Process store subscription payment"""
        try:
            self.session.begin_nested()
            
            # Get accounts and virtual accounts
            user_account = self.account_repo.get_by_id(user_account_id)
            app_account = self.account_repo.get_by_type("platform")
            
            user_virtual = self.account_repo.get_virtual_account(user_account_id)
            app_virtual = self.account_repo.get_virtual_account(app_account.id)
            
            if not all([user_account, app_account, user_virtual, app_virtual]):
                raise ValueError("Invalid account configuration")
            
            # Verify user has sufficient balance
            user_balance = await self.budpay_service.get_virtual_account_balance(
                user_virtual.account_number
            )
            if Decimal(str(user_balance["balance"])) < amount:
                raise ValueError("Insufficient funds")
            
            # Create transactions
            debit_txn = self.transaction_repo.create_transaction({
                "type": TransactionType.SUBSCRIPTION,
                "amount": amount,
                "description": f"Store subscription payment - Store ID: {store_id}",
                "status": TransactionStatus.PENDING,
                "account_id": user_account_id
            })
            
            credit_txn = self.transaction_repo.create_transaction({
                "type": TransactionType.SUBSCRIPTION,
                "amount": amount,
                "description": f"Subscription payment received - Store ID: {store_id}",
                "status": TransactionStatus.PENDING,
                "account_id": app_account.id,
                "reference": debit_txn.reference
            })
            
            try:
                # Transfer amount to platform's virtual account
                await self.budpay_service.transfer_to_virtual_account(
                    from_account=user_virtual.account_number,
                    to_account=app_virtual.account_number,
                    amount=amount,
                    description=f"Subscription payment for store {store_id}"
                )
                
                # Update account balances
                self.account_repo.debit_account(user_account, amount)
                self.account_repo.credit_account(app_account, amount)
                
                # Update transaction statuses
                for txn in [debit_txn, credit_txn]:
                    self.transaction_repo.update_status(
                        txn,
                        TransactionStatus.COMPLETED,
                        commit=False
                    )
                
                self.session.commit()
                
                return {
                    "status": "success",
                    "message": "Subscription payment processed successfully",
                    "data": {
                        "user_transaction": debit_txn,
                        "platform_transaction": credit_txn,
                        "amount": amount
                    }
                }
                
            except Exception as e:
                self.session.rollback()
                
                # Update transaction statuses to FAILED
                for txn in [debit_txn, credit_txn]:
                    self.transaction_repo.update_status(
                        txn,
                        TransactionStatus.FAILED,
                        commit=True
                    )
                
                raise e
            
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

    def get_transaction_history(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        type: Optional[TransactionType] = None,
        status: Optional[TransactionStatus] = None
    ) -> Dict:
        """Get user's transaction history"""
        return self.transaction_repo.get_user_transactions(
            user_id=user_id,
            skip=skip,
            limit=limit,
            type=type,
            status=status
        )