# repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from app.data.models.product_models import Product, ProductImage
from app.repository.base_repo import BaseRepository
from app.data.schemas.product_schemas import ProductBase
import uuid

class ProductRepository(BaseRepository[Product, ProductBase]):
    def __init__(self, session: Session):
        super().__init__(model=Product, session=session)

    def get_user_products(self, user_id: id) -> List[Product]:
        return self.session.query(self.model)\
            .filter(self.model.user_id == user_id)\
            .all()

    def get_product_by_id_and_user(self, product_id: id, user_id: id) -> Optional[Product]:
        return self.session.query(self.model)\
            .filter(self.model.id == product_id, self.model.user_id == user_id)\
            .first()

    def create_product_with_images(self, product: Product, images: List[ProductImage]) -> Product:
        """Create product with its images"""
        try:
            self.session.begin_nested()
            self.session.add(product)
            for image in images:
                self.session.add(image)
            self.session.commit()
            return product
        except Exception as e:
            self.session.rollback()
            raise e

    def update_product_images(self, product_id: id, new_images: List[ProductImage]) -> None:
        """Update product images"""
        try:
            self.session.begin_nested()
            # Delete existing images
            self.session.query(ProductImage)\
                .filter(ProductImage.product_id == product_id)\
                .delete()
            # Add new images
            for image in new_images:
                self.session.add(image)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e