from fastapi import Depends, status
from typing import List
from app.data.schemas.auth_schemas import ProtectedUser
from app.data.schemas.store_schemas import (
    StoreCreate,
    StoreRead,
    StoreUpdate,
)
from app.data.utils.database import get_db
from app.data.models.store_models import Store
from app.routes.base import BaseRouter
from app.service.store_service import StoreService
from sqlalchemy.orm import Session
from app.core.auth_dependency import get_current_user


class StoreRouter(BaseRouter[Store, StoreCreate, StoreRead, StoreService]):
    def __init__(self):
        super().__init__(
            service_class=StoreService,
            prefix="/stores",
            tags=["stores"]
        )
        self._register_store_routes()

    def _register_store_routes(self):
        @self.router.post(
            "/",
            response_model=StoreRead,
            status_code=status.HTTP_201_CREATED
        )
        async def create_store(
            store: StoreCreate,
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user),
        ):
            """Create a new store"""
            return self.service_class(session=db).create_store(
                user_id=current_user.id,
                store_data=store
            )

        @self.router.get(
            "/",
            response_model=List[StoreRead]
        )
        async def get_user_stores(
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user)
        ):
            """Get all stores for current user"""
            return self.service_class(session=db).get_user_stores(
                user_id=current_user.id
            )

        @self.router.put(
            "/{store_id}",
            response_model=StoreRead
        )
        async def update_store(
            store_id: int,
            store: StoreUpdate,
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user),
        ):
            """Update store information"""
            return self.service_class(session=db).update_store(
                user_id=current_user.id,
                store_id=store_id,
                store_data=store
            )

        @self.router.delete(
            "/{store_id}",
            status_code=status.HTTP_204_NO_CONTENT
        )
        async def delete_store(
            store_id: int,
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user)
        ):
            """Delete a store"""
            return self.service_class(session=db).delete_store(
                user_id=current_user.id,
                store_id=store_id
            )


# Initialize router
store_router = StoreRouter().router