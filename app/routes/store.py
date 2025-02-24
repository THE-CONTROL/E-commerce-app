# app/routes/store_routes.py
from fastapi import Depends, HTTPException, status, Body
from typing import List, Dict
from sqlalchemy.orm import Session
from app.data.schemas.auth_schemas import ProtectedUser
from app.data.schemas.store_schemas import (
    StoreCreate,
    StoreRead,
    StoreUpdate,
    SubscriptionRead
)
from app.core.constants import SUBSCRIPTION_PLANS, DurationType
from app.data.utils.database import get_db
from app.service.store_service import StoreService
from app.core.auth_dependency import get_current_user
from app.routes.base import BaseRouter
from app.data.models.store_models import Store


class StoreRouter(BaseRouter[Store, StoreCreate, StoreUpdate, StoreService]):
    def __init__(self):
        super().__init__(
            service_class=StoreService,
            prefix="/stores",
            tags=["stores"],
            protected=True
        )
        self._register_store_routes()

    def _register_store_routes(self):
        @self.router.get(
            "/subscriptions",
            response_model=List[SubscriptionRead],
            summary="Get Available Subscriptions",
            description="Get available store subscription plans"
        )
        async def get_subscriptions():
            return [
                SubscriptionRead(**plan)
                for plan in SUBSCRIPTION_PLANS.values()
            ]

        @self.router.post(
            "/",
            response_model=StoreRead,
            status_code=status.HTTP_201_CREATED,
            summary="Create Store",
            description="Create a new store with subscription payment"
        )
        async def create_store(
            store: StoreCreate,
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user)
        ):
            try:
                result = await self.service_class(session=db).create_store(
                    user_id=current_user.id,
                    store_data=store
                )
                return result
            except HTTPException as e:
                raise e
            except Exception as error:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(error)
                )

        @self.router.post(
            "/{store_id}/renew",
            response_model=Dict,
            summary="Renew Subscription",
            description="Renew store subscription with payment"
        )
        async def renew_subscription(
            store_id: int,
            subscription_id: int = Body(...),
            duration_type: DurationType = Body(...),
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user)
        ):
            try:
                result = await self.service_class(session=db).renew_subscription(
                    user_id=current_user.id,
                    store_id=store_id,
                    subscription_id=subscription_id,
                    duration_type=duration_type
                )
                return result
            except HTTPException as e:
                raise e
            except Exception as error:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(error)
                )

        @self.router.get(
            "/my-store",
            response_model=StoreRead,
            summary="Get User Store",
            description="Get authenticated user's store"
        )
        async def get_user_store(
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user)
        ):
            try:
                return self.service_class(session=db).get_user_store(current_user.id)
            except HTTPException as e:
                raise e
            except Exception as error:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(error)
                )

        @self.router.put(
            "/my-store",
            response_model=StoreRead,
            summary="Update Store",
            description="Update store details (non-subscription updates)"
        )
        async def update_store(
            store: StoreUpdate,
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user)
        ):
            try:
                service = self.service_class(session=db)
                existing_store = service.get_user_store(current_user.id)
                
                return service.update_store(
                    user_id=current_user.id,
                    store_id=existing_store.id,
                    store_data=store
                )
            except HTTPException as e:
                raise e
            except Exception as error:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(error)
                )

        @self.router.delete(
            "/my-store",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Delete Store",
            description="Delete user's store"
        )
        async def delete_store(
            db: Session = Depends(get_db),
            current_user: ProtectedUser = Depends(get_current_user)
        ):
            try:
                service = self.service_class(session=db)
                store = service.get_user_store(current_user.id)
                
                service.delete_store(
                    user_id=current_user.id,
                    store_id=store.id
                )
            except HTTPException as e:
                raise e
            except Exception as error:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(error)
                )

# Initialize router
store_router = StoreRouter().router