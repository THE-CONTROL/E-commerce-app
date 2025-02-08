from fastapi import Depends, Security, status
from typing import List
from app.data.schemas.auth_schemas import ProtectedUser
from app.data.schemas.product_schemas import (
    ProductCreate,
    ProductRead,
    ProductUpdate
)
from app.data.utils.database import get_db
from app.data.models.product_models import Product
from app.routes.base import BaseRouter
from app.service.product_service import ProductService
from sqlalchemy.orm import Session
from app.core.auth_dependency import get_current_user


class ProductRouter(BaseRouter[Product, ProductCreate, ProductRead, ProductService]):
    def __init__(self):
        super().__init__(
            service_class=ProductService,
            prefix="/products",
            tags=["products"]
        )
        self.product_service = ProductService
        self._register_product_routes()

    def _register_product_routes(self):
        @self.router.post(
            "/{store_id}/products",
            response_model=ProductRead,
            status_code=status.HTTP_201_CREATED
        )
        async def create_product(
            store_id: int,
            product: ProductCreate,
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user),
        ):
            """Create a new product in store"""
            return self.product_service(session=db).create_product(
                user_id=current_user.id,
                store_id=store_id,
                product_data=product
            )

        @self.router.get(
            "/{store_id}/products",
            response_model=List[ProductRead]
        )
        async def get_store_products(
            store_id: int,
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user),
        ):
            """Get all products in a store"""
            return self.product_service(session=db).get_store_products(
                user_id=current_user.id,
                store_id=store_id
            )
            
        @self.router.put(
            "/{store_id}/products/{product_id}",
            response_model=ProductRead
        )
        async def update_product(
            store_id: int,
            product_id: int,
            product: ProductUpdate,
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user),
        ):
            """Update product information"""
            return self.product_service(session=db).update_product(
                user_id=current_user.id,
                store_id=store_id,
                product_id=product_id,
                product_data=product
            )

        @self.router.delete(
            "/{store_id}/products/{product_id}",
            status_code=status.HTTP_204_NO_CONTENT
        )
        async def delete_product(
            store_id: int,
            product_id: int,
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user),
        ):
            """Delete a product"""
            return self.product_service(session=db).delete_product(
                user_id=current_user.id,
                store_id=store_id,
                product_id=product_id
            )


# Initialize router
store_router = ProductRouter().router