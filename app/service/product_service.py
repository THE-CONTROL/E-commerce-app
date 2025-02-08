from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.data.models.product_models import Product
from app.repository.product_repo import ProductRepository
from app.repository.store_repo import StoreRepository
from app.service.base_service import BaseService
from app.data.schemas.product_schemas import ProductCreate, ProductUpdate


class ProductService(BaseService[Product, ProductCreate, ProductUpdate]):
    def __init__(self, session: Session):
        super().__init__(repository=ProductRepository(session=session))
        self.store_repository = StoreRepository(session=session)
        self.session = session

    def create_product(self, user_id: int, store_id: int, product_data: ProductCreate) -> Product:
        """Create a new product in store"""
        store = self.store_repository.get_store_by_id_and_user(store_id, user_id)
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found"
            )

        product = Product(**product_data.model_dump(), store_id=store_id)
        return self.repository.create(product)

    def get_store_products(self, user_id: int, store_id: int) -> List[Product]:
        """Get all products in a store"""
        store = self.store_repository.get_store_by_id_and_user(store_id, user_id)
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found"
            )
        
        return self.repository.get_store_products(store_id)

    def update_product(self, user_id: int, store_id: int, product_id: int, product_data: ProductUpdate) -> Product:
        """Update product information"""
        store = self.store_repository.get_store_by_id_and_user(store_id, user_id)
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found"
            )

        product = self.repository.get_product_by_id_and_store(product_id, store_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        for field, value in product_data.model_dump(exclude_unset=True).items():
            setattr(product, field, value)
        
        return self.repository.update(product)

    def delete_product(self, user_id: int, store_id: int, product_id: int) -> None:
        """Delete a product"""
        store = self.store_repository.get_store_by_id_and_user(store_id, user_id)
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found"
            )

        product = self.repository.get_product_by_id_and_store(product_id, store_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        self.repository.delete(product)