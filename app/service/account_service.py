from datetime import datetime
from typing import Dict
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.repository.account_repo import AccountRepository
from app.repository.transaction_repo import TransactionRepository
from app.service.budpay_service import BudpayService
from app.data.models.transaction_models import TransactionType, TransactionStatus
from app.data.models.account_models import Account, VirtualBankAccount, AccountType


class AccountService:
    def __init__(self, session: Session):
        """Initialize service with database session"""
        self.session = session
        self.account_repo = AccountRepository(session)
        self.transaction_repo = TransactionRepository(session)
        self.budpay_service = BudpayService()

    def _generate_account_key(self, user_id: int) -> str:
        """Generate unique account identifier"""
        from datetime import datetime
        import uuid
        
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        random_str = uuid.uuid4().hex[:6].upper()
        user_str = str(user_id).zfill(6)
        
        return f"ACC-{timestamp}-{user_str}-{random_str}"
    
    async def create_account_with_virtual(
        self,
        user_id: int,
        profile_data: dict
    ) -> Dict:
        """
        Create new account with virtual account for user.
        A user can only have one account.
        """
        try:
            # Check if user already has an account
            existing_account = self.account_repo.get_user_account(user_id)
            if existing_account:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already has an account"
                )
            
            # Create Budpay virtual account
            budpay_account = await self.budpay_service.create_virtual_account(
                email=profile_data["email"],
                first_name=profile_data["first_name"],
                last_name=profile_data["last_name"],
                phone=profile_data["phone"]
            )

            # Prepare account data
            account_data = {
                "user_id": user_id,
                "type": AccountType.USER,
                "key": self._generate_account_key(user_id),
                "currency": "NGN",
                "balance": 0,
                "is_fundable": True,
                "is_withdrawable": True,
                "is_suspended": False,
                "locked": False
            }
            
            # Prepare virtual account data
            virtual_account_data = {
                "account_number": budpay_account["account_number"],
                "account_name": budpay_account["account_name"],
                "bank_name": budpay_account["bank_name"],
                "bank_code": budpay_account["bank_code"],
                "email": profile_data["email"],
                "phone": profile_data["phone"],
                "reference": budpay_account["reference"]
            }
            
            # Create account and virtual account
            account, virtual_account = self.account_repo.create_with_virtual_account(
                account_data=account_data,
                virtual_account_data=virtual_account_data
            )
            
            return {
                "account": account,
                "virtual_account": virtual_account,
                "budpay_details": budpay_account
            }
            
        except HTTPException as e:
            raise e
        except SQLAlchemyError as e:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    def get_user_account(self, user_id: int) -> Account:
        """Get a user's account"""
        try:
            account = self.account_repo.get_user_account(user_id)
            if not account:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Account not found"
                )
            return account
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    def get_virtual_account(self, user_id: int) -> VirtualBankAccount:
        """Get a user's virtual account details"""
        try:
            account = self.get_user_account(user_id)
            virtual_account = account.active_virtual_account
            
            if not virtual_account:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No active virtual account found"
                )
            return virtual_account
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    def _validate_webhook_data(self, body: Dict) -> tuple[str, Decimal, str]:
        """Validate webhook payload and extract required data"""
        # Extract account number
        account_data = body.get("account", {})
        account_number = account_data.get("account_number")
        if not account_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing account number in webhook"
            )

        # Validate amount
        try:
            amount = Decimal(str(body.get("amount", 0)))
            if amount <= 0:
                raise ValueError()
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid amount in webhook"
            )

        # Get reference
        reference = body.get("reference")
        if not reference:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing reference in webhook"
            )

        return account_number, amount, reference

    async def process_webhook(
        self,
        signature: str,
        payload: bytes,
        body: Dict
    ) -> Dict:
        """Process virtual account webhook from Budpay"""
        try:
            # Verify webhook signature
            if not self.budpay_service.verify_webhook_signature(signature, payload):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid webhook signature"
                )

            # Validate webhook data
            account_number, amount, reference = self._validate_webhook_data(body)

            # Get associated account
            account = self.account_repo.get_by_virtual_account(account_number)
            if not account:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Account not found"
                )

            # Check for duplicate transaction
            existing_txn = self.transaction_repo.get_by_reference(reference)
            if existing_txn:
                return {
                    "status": "success",
                    "message": "Transaction already processed",
                    "data": existing_txn
                }

            # Process transaction
            with self.session.begin_nested():
                # Create transaction record
                transaction = self.transaction_repo.create_transaction({
                    "type": TransactionType.CREDIT,
                    "amount": amount,
                    "description": "Virtual Account Credit",
                    "status": TransactionStatus.COMPLETED,
                    "reference": reference,
                    "account_id": account.id,
                    "completed_at": datetime.utcnow()
                })

                # Update account balance
                self.account_repo.credit_account(account, amount)

            # Commit transaction
            self.session.commit()

            return {
                "status": "success",
                "message": "Payment processed successfully",
                "data": transaction
            }

        except HTTPException as e:
            raise e
        except SQLAlchemyError as e:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )