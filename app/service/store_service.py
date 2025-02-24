from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.data.models.store_models import Store, StoreSubscription
from app.repository.account_repo import AccountRepository
from app.repository.store_repo import StoreRepository
from app.service.base_service import BaseService
from app.data.schemas.store_schemas import StoreCreate, StoreUpdate
from app.repository.user_repo import UserRepository
from app.core.constants import SUBSCRIPTION_PLANS, DurationType
from app.service.transaction_service import TransactionService


class StoreService(BaseService[Store, StoreCreate, StoreUpdate]):
    def __init__(self, session: Session):
        super().__init__(repository=StoreRepository(session=session))
        self.user_repo = UserRepository(session=session)
        self.account_repo = AccountRepository(session=session)
        self.transaction_service = TransactionService(session=session)
        self.session = session

    async def create_store(self, user_id: int, store_data: StoreCreate) -> Store:
        """Create a new store with subscription payment"""
        try:
            # Start transaction
            self.session.begin_nested()

            # Validate user
            user = self.user_repo.get_user_by_id(user_id)
            if user.is_suspended:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User is suspended"
                )

            # Check if user already has a store
            if self._repository.has_active_store(user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already has an active store"
                )

            # Get subscription plan
            subscription_plan = next(
                (plan for plan in SUBSCRIPTION_PLANS.values() if plan["id"] == store_data.subscription_id),
                None
            )
            if not subscription_plan:
                print(store_data.subscription_id)
                print(SUBSCRIPTION_PLANS)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid subscription plan"
                )

            # Get subscription amount based on duration type
            amount = (
                Decimal(str(subscription_plan['yearly_amount']))
                if store_data.duration_type == DurationType.YEARLY
                else Decimal(str(subscription_plan['monthly_amount']))
            )

            # Create store (initially inactive)
            store_dict = store_data.model_dump(exclude={'subscription_id', 'duration_type'})
            store = Store(
                user_id=user_id,
                **store_dict
            )
            self.session.add(store)
            self.session.flush()  # Get store ID

            # Calculate subscription dates
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(
                days=365 if store_data.duration_type == DurationType.YEARLY else 30
            )

            # Create subscription (initially inactive)
            subscription = StoreSubscription(
                store_id=store.id,
                subscription_id=store_data.subscription_id,
                start_date=start_date,
                end_date=end_date,
                is_active=False  # Will be activated after payment
            )
            self.session.add(subscription)

            # Process payment
            user_account = self.account_repo.get_user_account(user_id)
            if not user_account:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User account not found"
                )

            # Process subscription payment
            payment_result = await self.transaction_service.process_subscription_payment(
                user_account_id=user_account.id,
                store_id=store.id,
                amount=amount
            )

            if payment_result["status"] == "success":
                # Activate subscription
                subscription.is_active = True
                self.session.add(subscription)
                self.session.commit()

                return store
            else:
                self.session.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Subscription payment failed"
                )

        except Exception as e:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def renew_subscription(
        self,
        user_id: int,
        store_id: int,
        subscription_id: int,
        duration_type: DurationType
    ) -> Dict:
        """Renew store subscription"""
        try:
            self.session.begin_nested()

            # Get store and current subscription
            store = self._repository.get_store_by_id_and_user(store_id, user_id)
            if not store:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Store not found"
                )

            # Get subscription plan
            subscription_plan = SUBSCRIPTION_PLANS.get(subscription_id)
            if not subscription_plan:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid subscription plan"
                )

            # Calculate amount
            amount = (
                Decimal(str(subscription_plan['yearly_amount']))
                if duration_type == DurationType.YEARLY
                else Decimal(str(subscription_plan['monthly_amount']))
            )

            # Process payment
            user_account = self.account_repo.get_user_account(user_id)
            if not user_account:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User account not found"
                )

            # Process subscription payment
            payment_result = await self.transaction_service.process_subscription_payment(
                user_account_id=user_account.id,
                store_id=store_id,
                amount=amount
            )

            if payment_result["status"] == "success":
                # Update subscription
                current_subscription = self._repository.get_store_subscription(store_id)
                
                # Calculate new dates
                start_date = current_subscription.end_date  # Start from end of current subscription
                end_date = start_date + timedelta(
                    days=365 if duration_type == DurationType.YEARLY else 30
                )

                current_subscription.subscription_id = subscription_id
                current_subscription.start_date = start_date
                current_subscription.end_date = end_date
                current_subscription.is_active = True

                self.session.add(current_subscription)
                self.session.commit()

                return {
                    "message": "Subscription renewed successfully",
                    "store": store,
                    "subscription": current_subscription,
                    "payment": payment_result
                }
            else:
                self.session.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Subscription payment failed"
                )

        except Exception as e:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    def get_user_store(self, user_id: str) -> Store:
        """Get user's store"""
        store = self._repository.get_user_store(user_id)
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found"
            )
        return store

    def update_store(self, user_id: str, store_id: str, store_data: StoreUpdate) -> Store:
        """Update store information"""
        store = self._repository.get_store_by_id_and_user(store_id, user_id)
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found"
            )
        
        update_data = store_data.model_dump(exclude_unset=True)
        
        # Handle subscription update
        if 'subscription_id' in update_data:
            if update_data['subscription_id'] not in [plan['id'] for plan in SUBSCRIPTION_PLANS.values()]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid subscription plan"
                )
                
            subscription = self._repository.get_store_subscription(store_id)
            if subscription:
                subscription.subscription_id = update_data.pop('subscription_id')
                self.session.add(subscription)
        
        # Update store
        for field, value in update_data.items():
            setattr(store, field, value)
        
        self.session.add(store)
        self.session.commit()
        return store

    def delete_store(self, user_id: str, store_id: str) -> None:
        """Delete a store"""
        store = self._repository.get_store_by_id_and_user(store_id, user_id)
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found"
            )
        
        self._repository.delete(store)