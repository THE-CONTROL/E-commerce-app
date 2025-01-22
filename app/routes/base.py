from fastapi import APIRouter, Depends
from typing import Generic, TypeVar, Type
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.auth_dependency import get_current_user
from app.data.utils.database import get_db
from app.service.base_service import BaseService


ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ServiceType = TypeVar("ServiceType", bound=BaseService)

class BaseRouter(Generic[ModelType, CreateSchemaType, UpdateSchemaType, ServiceType]):
    def __init__(
        self,
        service_class: Type[ServiceType],
        prefix: str,
        tags: list[str],
        protected: bool = True
    ):
        self.router = APIRouter(prefix=prefix, tags=tags)
        self.service_class = service_class
        self.protected = protected
        self._register_routes()

    def _register_routes(self):
        if self.protected:
            # Protected routes (require authentication)
            @self.router.get("/", response_model=ModelType)
            async def get_item(
                current_user=Depends(get_current_user),
                db: Session = Depends(get_db)
            ):
                try:
                    return self.service_class(session=db).get_by_id(id=current_user.id)
                except Exception as error:
                    raise error

            @self.router.put("/", response_model=dict)
            async def update_item(
                update_data: UpdateSchemaType,
                current_user=Depends(get_current_user),
                db: Session = Depends(get_db)
            ):
                try:
                    return self.service_class(session=db).update(
                        id=current_user.id,
                        data=update_data
                    )
                except Exception as error:
                    raise error

            @self.router.delete("/", response_model=dict)
            async def delete_item(
                current_user=Depends(get_current_user),
                db: Session = Depends(get_db)
            ):
                try:
                    return self.service_class(session=db).delete(id=current_user.id)
                except Exception as error:
                    raise error
        else:
            # Public routes (no authentication required)
            @self.router.get("/{item_id}", response_model=ModelType)
            async def get_item(
                item_id: int,
                db: Session = Depends(get_db)
            ):
                try:
                    return self.service_class(session=db).get_by_id(id=item_id)
                except Exception as error:
                    raise error

            @self.router.put("/{item_id}", response_model=dict)
            async def update_item(
                item_id: int,
                update_data: UpdateSchemaType,
                db: Session = Depends(get_db)
            ):
                try:
                    return self.service_class(session=db).update(
                        id=item_id,
                        data=update_data
                    )
                except Exception as error:
                    raise error

            @self.router.delete("/{item_id}", response_model=dict)
            async def delete_item(
                item_id: int,
                db: Session = Depends(get_db)
            ):
                try:
                    return self.service_class(session=db).delete(id=item_id)
                except Exception as error:
                    raise error