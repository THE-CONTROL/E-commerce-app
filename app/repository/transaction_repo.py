# app/repository/transaction_repo.py
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from app.data.models.account_models import Account
from app.data.models.transaction_models import Transaction, TransactionStatus, TransactionType
from sqlalchemy.orm import Session
from sqlalchemy import and_

class TransactionRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_transaction(self, data: Dict) -> Transaction:
        """Create a new transaction"""
        try:
            # Generate reference if not provided
            if 'reference' not in data:
                data['reference'] = self._generate_reference()
            
            # Set timestamps
            now = datetime.utcnow()
            data['created_at'] = now
            data['updated_at'] = now
            
            # Create transaction
            transaction = Transaction(**data)
            self.session.add(transaction)
            self.session.flush()
            return transaction
        
        except Exception as e:
            self.session.rollback()
            raise e

    def update_status(
        self, 
        transaction: Transaction,
        status: TransactionStatus,
        commit: bool = True
    ) -> Transaction:
        """Update transaction status"""
        try:
            transaction.status = status
            transaction.updated_at = datetime.utcnow()
            
            if status == TransactionStatus.COMPLETED:
                transaction.completed_at = datetime.utcnow()
            
            self.session.add(transaction)
            if commit:
                self.session.commit()
            return transaction
            
        except Exception as e:
            if commit:
                self.session.rollback()
            raise e

    def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Get transaction by ID"""
        return self.session.query(Transaction).get(transaction_id)

    def get_by_reference(self, reference: str) -> Optional[Transaction]:
        """Get transaction by reference"""
        return self.session.query(Transaction).filter(
            Transaction.reference == reference
        ).first()

    def get_account_transactions(
        self,
        account_id: int,
        skip: int = 0,
        limit: int = 50,
        type: Optional[TransactionType] = None,
        status: Optional[TransactionStatus] = None
    ) -> Tuple[List[Transaction], int]:
        """Get transactions for an account with filters"""
        # Build base query
        query = self.session.query(Transaction).filter(
            Transaction.account_id == account_id
        )

        # Apply filters if provided
        filters = []
        if type:
            filters.append(Transaction.type == type)
        if status:
            filters.append(Transaction.status == status)
        
        if filters:
            query = query.filter(and_(*filters))

        # Get total count
        total = query.count()

        # Get paginated results
        transactions = query.order_by(
            Transaction.created_at.desc()
        ).offset(skip).limit(limit).all()

        return transactions, total

    def get_user_transactions(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        type: Optional[TransactionType] = None,
        status: Optional[TransactionStatus] = None
    ) -> Dict:
        """Get all transactions linked to user's accounts"""
        # Get all user's account IDs
        account_ids = self.session.query(Account.id).filter(
            Account.user_id == user_id
        ).all()
        account_ids = [acc.id for acc in account_ids]
        
        # Build base query
        query = self.session.query(Transaction).filter(
            Transaction.account_id.in_(account_ids)
        )
        
        # Apply filters if provided
        filters = []
        if type:
            filters.append(Transaction.type == type)
        if status:
            filters.append(Transaction.status == status)
        
        if filters:
            query = query.filter(and_(*filters))
            
        # Get total count
        total = query.count()
        
        # Get paginated results with ordering
        transactions = query.order_by(
            Transaction.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return {
            "data": transactions,
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit
        }

    def _generate_reference(self) -> str:
        """Generate unique transaction reference"""
        import uuid
        from datetime import datetime
        
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        random_str = uuid.uuid4().hex[:8].upper()
        reference = f"TXN-{timestamp}-{random_str}"
        
        # Ensure uniqueness
        while self.get_by_reference(reference):
            random_str = uuid.uuid4().hex[:8].upper()
            reference = f"TXN-{timestamp}-{random_str}"
        
        return reference

    def get_related_transactions(self, reference: str) -> List[Transaction]:
        """Get all transactions with the same reference (e.g., all parts of a payment)"""
        return self.session.query(Transaction).filter(
            Transaction.reference == reference
        ).order_by(Transaction.created_at.asc()).all()

    def get_transactions_by_type_and_status(
        self,
        account_id: int,
        types: List[TransactionType],
        status: TransactionStatus,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Transaction]:
        """Get transactions by type and status with optional date range"""
        query = self.session.query(Transaction).filter(
            and_(
                Transaction.account_id == account_id,
                Transaction.type.in_(types),
                Transaction.status == status
            )
        )

        if start_date:
            query = query.filter(Transaction.created_at >= start_date)
        if end_date:
            query = query.filter(Transaction.created_at <= end_date)

        return query.order_by(Transaction.created_at.desc()).all()

    def get_transaction_summary(
        self,
        account_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """Get transaction summary for an account"""
        from sqlalchemy import func
        
        # Base query
        query = self.session.query(
            Transaction.type,
            func.count(Transaction.id).label('count'),
            func.sum(Transaction.amount).label('total_amount'),
            func.sum(Transaction.fee_amount).label('total_fees')
        ).filter(
            Transaction.account_id == account_id,
            Transaction.status == TransactionStatus.COMPLETED
        )

        # Apply date filters if provided
        if start_date:
            query = query.filter(Transaction.created_at >= start_date)
        if end_date:
            query = query.filter(Transaction.created_at <= end_date)

        # Group by transaction type
        results = query.group_by(Transaction.type).all()

        # Format results
        summary = {}
        for type_, count, total_amount, total_fees in results:
            summary[type_] = {
                'count': count,
                'total_amount': float(total_amount or 0),
                'total_fees': float(total_fees or 0)
            }

        return summary