# app/service/account_service.py
from datetime import datetime
from typing import Dict
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repository.account_repo import AccountRepository
from app.repository.transaction_repo import TransactionRepository
from app.service.budpay_service import BudpayService
from app.data.models.transaction_models import TransactionType, TransactionStatus

class AccountService:
    def __init__(self, session: Session):
        self.session = session
        self.account_repo = AccountRepository(session)
        self.transaction_repo = TransactionRepository(session)
        self.budpay_service = BudpayService()

    async def create_account_with_virtual(
        self,
        user_id: int,
        account_type: str,
        profile_data: dict
    ) -> dict:
        """Create account with Budpay virtual account"""
        try:
            # Create Budpay virtual account
            budpay_account = await self.budpay_service.create_virtual_account(
                email=profile_data["email"],
                first_name=profile_data["first_name"],
                last_name=profile_data["last_name"],
                phone=profile_data["phone"]
            )
            
            # Create accounts
            account_data = {
                "user_id": user_id,
                "type": account_type,
                "key": self._generate_unique_account_key(user_id)
            }
            
            virtual_account_data = {
                "account_number": budpay_account["account_number"],
                "account_name": budpay_account["account_name"],
                "bank_name": budpay_account["bank_name"],
                "bank_code": budpay_account["bank_code"],
                "email": profile_data["email"],
                "phone": profile_data["phone"],
                "reference": budpay_account["reference"]
            }
            
            account, virtual_account = self.account_repo.create_with_virtual_account(
                account_data,
                virtual_account_data
            )
            
            return {
                "account": account,
                "virtual_account": virtual_account,
                "budpay_details": budpay_account
            }
            
        except Exception as e:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    def _generate_unique_account_key(self, user_id: int) -> str:
        """Generate unique account key"""
        import uuid
        from datetime import datetime
        
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        random_str = uuid.uuid4().hex[:6].upper()
        user_part = str(user_id).zfill(6)
        
        return f"ACC-{timestamp}-{user_part}-{random_str}"

    async def process_webhook(
        self,
        signature: str,
        payload: bytes,
        body: Dict
    ) -> Dict:
        """Process Budpay webhook for virtual account transactions"""
        if not self.budpay_service.verify_webhook_signature(signature, payload):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid webhook signature"
            )
            
        try:
            # Get account from virtual account number
            virtual_account_number = body.get("account", {}).get("account_number")
            if not virtual_account_number:
                raise ValueError("Missing account number")
                
            account = self.account_repo.get_by_virtual_account(virtual_account_number)
            if not account:
                raise ValueError("Account not found")
                
            amount = Decimal(str(body.get("amount", 0)))
            if amount <= 0:
                raise ValueError("Invalid amount")
                
            reference = body.get("reference")
            if not reference:
                raise ValueError("Missing reference")
                
            # Check if transaction already processed
            existing_transaction = self.transaction_repo.get_by_reference(reference)
            if existing_transaction:
                return {
                    "status": "success",
                    "message": "Transaction already processed",
                    "data": existing_transaction
                }
                
            # Create transaction
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
            
            return {
                "status": "success",
                "message": "Payment processed successfully",
                "data": transaction
            }
            
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