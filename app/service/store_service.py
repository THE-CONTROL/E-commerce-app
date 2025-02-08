from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.data.models.store_models import Store
from app.repository.store_repo import StoreRepository
from app.repository.product_repo import ProductRepository
from app.service.base_service import BaseService
from app.data.schemas.store_schemas import StoreCreate, StoreUpdate
from app.repository.user_repo import UserRepository


class StoreService(BaseService[Store, StoreCreate, StoreUpdate]):
    def __init__(self, session: Session):
        super().__init__(repository=StoreRepository(session=session))
        self.product_repository = ProductRepository(session=session)
        self.user_repo = UserRepository(session=session)
        self.session = session

    def create_store(self, user_id: int, store_data: StoreCreate) -> Store:
        """Create a new store for user"""
        # Check if user is subscribed
        user = self.user_repo.get_user_by_id(user_id)
        if not user.verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User must be subscribed to create stores"
            )

        store = Store(**store_data.model_dump(), user_id=user_id)
        return self.repository.create(store)

    def get_user_stores(self, user_id: int) -> List[Store]:
        # Check if user is subscribed
        user = self.user_repo.get_user_by_id(user_id)
        if not user.verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User must be subscribed to create stores"
            )
        """Get all stores for a user"""
        return self.repository.get_user_stores(user_id)

    def update_store(self, user_id: int, store_id: int, store_data: StoreUpdate) -> Store:
        # Check if user is subscribed
        user = self.user_repo.get_user_by_id(user_id)
        if not user.verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User must be subscribed to create stores"
            )
        """Update store information"""
        store = self.repository.get_store_by_id_and_user(store_id, user_id)
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found"
            )
        
        for field, value in store_data.model_dump(exclude_unset=True).items():
            setattr(store, field, value)
        
        return self.repository.update(store)

    def delete_store(self, user_id: int, store_id: int) -> None:
        # Check if user is subscribed
        user = self.user_repo.get_user_by_id(user_id)
        if not user.verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User must be subscribed to create stores"
            )
        """Delete a store"""
        store = self.repository.get_store_by_id_and_user(store_id, user_id)
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found"
            )
        
        self.repository.delete(store)
