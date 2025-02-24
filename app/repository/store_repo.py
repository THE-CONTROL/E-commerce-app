from typing import Optional
from sqlalchemy.orm import Session
from app.data.models.store_models import Store, StoreSubscription
from app.repository.base_repo import BaseRepository
from app.data.schemas.store_schemas import StoreBase
from sqlalchemy import and_


class StoreRepository(BaseRepository[Store, StoreBase]):
    def __init__(self, session: Session):
        super().__init__(model=Store, session=session)

    def get_user_store(self, user_id: str) -> Optional[Store]:
        """Get user's store (single store per user)"""
        return self.session.query(self.model)\
            .filter(self.model.user_id == user_id)\
            .first()

    def has_active_store(self, user_id: str) -> bool:
        """Check if user has an active store"""
        return self.session.query(self.model)\
            .join(StoreSubscription)\
            .filter(
                and_(
                    Store.user_id == user_id,
                    StoreSubscription.is_active == True
                )
            ).first() is not None

    def get_store_by_id_and_user(self, store_id: str, user_id: str) -> Optional[Store]:
        return self.session.query(self.model)\
            .filter(self.model.id == store_id, self.model.user_id == user_id)\
            .first()

    def get_store_subscription(self, store_id: str) -> Optional[StoreSubscription]:
        return self.session.query(StoreSubscription)\
            .filter(StoreSubscription.store_id == store_id)\
            .first()

    def create_store_with_subscription(self, store: Store, subscription: StoreSubscription) -> Store:
        """Create store with its subscription"""
        try:
            self.session.begin_nested()
            self.session.add(store)
            self.session.add(subscription)
            self.session.commit()
            return store
        except Exception as e:
            self.session.rollback()
            raise e