# service.py
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.data.models.product_models import Product, ProductImage
from app.repository.product_repo import ProductRepository
from app.service.base_service import BaseService
from app.data.schemas.product_schemas import ProductCreate, ProductUpdate
import uuid

class ProductService(BaseService[Product, ProductCreate, ProductUpdate]):
    def __init__(self, session: Session):
        super().__init__(repository=ProductRepository(session=session))
        self.session = session

    def create_product(self, user_id: int, product_data: ProductCreate) -> Product:
        """Create a new product with images"""
        # Create product
        product = Product(
            user_id=user_id,
            **product_data.model_dump(exclude={'images'})
        )

        # Create product images
        images = [
            ProductImage(
                product_id=product.id,
                **image.model_dump()
            )
            for image in product_data.images
        ]

        # Ensure one primary image
        primary_images = [img for img in images if img.is_primary]
        if not primary_images:
            images[0].is_primary = True
        elif len(primary_images) > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only one primary image allowed"
            )

        return self._repository.create_product_with_images(product, images)

    def get_user_products(self, user_id: int) -> List[Product]:
        """Get all products for a user"""
        return self._repository.get_user_products(user_id)

    def update_product(self, user_id: int, product_id: int, product_data: ProductUpdate) -> Product:
        """Update product information and images"""
        product = self._repository.get_product_by_id_and_user(product_id, user_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        update_data = product_data.model_dump(exclude_unset=True)
        
        # Handle images update if provided
        if 'images' in update_data:
            images = [
                ProductImage(
                    **image.model_dump()
                )
                for image in update_data.pop('images')
            ]
            
            # Validate primary image
            primary_images = [img for img in images if img.is_primary]
            if not primary_images:
                images[0].is_primary = True
            elif len(primary_images) > 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only one primary image allowed"
                )
                
            self._repository.update_product_images(product_id, images)

        # Update product fields
        for field, value in update_data.items():
            setattr(product, field, value)
        
        self.session.add(product)
        self.session.commit()
        return product

    def delete_product(self, user_id: int, product_id: int) -> None:
        """Delete a product and its images"""
        product = self._repository.get_product_by_id_and_user(product_id, user_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        self._repository.delete(product)