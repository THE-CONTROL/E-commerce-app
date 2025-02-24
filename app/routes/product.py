# router.py
from fastapi import Depends, status
from typing import List
from app.data.schemas.auth_schemas import ProtectedUser
from app.data.schemas.product_schemas import (
    ProductCreate,
    ProductRead,
    ProductUpdate
)
from app.data.utils.database import get_db
from app.routes.base import BaseRouter
from app.service.product_service import ProductService
from sqlalchemy.orm import Session
from app.core.auth_dependency import get_current_user

class ProductRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            service_class=ProductService,
            prefix="/products",
            tags=["products"],
            protected=True
        )
        self._register_product_routes()

    def _register_product_routes(self):
        @self.router.post(
            "/",
            response_model=ProductRead,
            status_code=status.HTTP_201_CREATED,
            summary="Create Product",
            description="Create a new product with images"
        )
        async def create_product(
            product: ProductCreate,
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user),
        ):
            return self.service_class(session=db).create_product(
                user_id=current_user.id,
                product_data=product
            )

        @self.router.get(
            "/",
            response_model=List[ProductRead],
            summary="Get User Products",
            description="Get all products for the authenticated user"
        )
        async def get_user_products(
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user),
        ):
            return self.service_class(session=db).get_user_products(
                user_id=current_user.id
            )
            
        @self.router.put(
            "/{product_id}",
            response_model=ProductRead,
            summary="Update Product",
            description="Update product information and images"
        )
        async def update_product(
            product_id: int,
            product: ProductUpdate,
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user),
        ):
            return self.service_class(session=db).update_product(
                user_id=current_user.id,
                product_id=product_id,
                product_data=product
            )

        @self.router.delete(
            "/{product_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Delete Product",
            description="Delete a product and its images"
        )
        async def delete_product(
            product_id: int,
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user),
        ):
            self.service_class(session=db).delete_product(
                user_id=current_user.id,
                product_id=product_id
            )

# Initialize router
product_router = ProductRouter().router