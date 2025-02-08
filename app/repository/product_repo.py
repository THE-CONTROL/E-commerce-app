from typing import List, Optional
from sqlalchemy.orm import Session
from app.data.models.product_models import Product
from app.repository.base_repo import BaseRepository
from app.data.schemas.product_schemas import ProductBase


class ProductRepository(BaseRepository[Product, ProductBase]):
    def __init__(self, session: Session):
        super().__init__(model=Product, session=session)

    def get_store_products(self, store_id: int) -> List[Product]:
        return self.session.query(self.model)\
            .filter(self.model.store_id == store_id)\
            .all()

    def get_product_by_id_and_store(self, product_id: int, store_id: int) -> Optional[Product]:
        return self.session.query(self.model)\
            .filter(self.model.id == product_id, self.model.store_id == store_id)\
            .first()