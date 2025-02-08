from typing import List, Optional
from sqlalchemy.orm import Session
from app.data.models.store_models import Store
from app.repository.base_repo import BaseRepository
from app.data.schemas.store_schemas import StoreBase


class StoreRepository(BaseRepository[Store, StoreBase]):
    def __init__(self, session: Session):
        super().__init__(model=Store, session=session)

    def get_user_stores(self, user_id: int) -> List[Store]:
        return self.session.query(self.model)\
            .filter(self.model.user_id == user_id)\
            .all()

    def get_store_by_id_and_user(self, store_id: int, user_id: int) -> Optional[Store]:
        return self.session.query(self.model)\
            .filter(self.model.id == store_id, self.model.user_id == user_id)\
            .first()
