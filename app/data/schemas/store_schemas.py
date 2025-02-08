from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.data.schemas.product_schemas import ProductRead


class StoreBase(BaseModel):
    name: str
    description: Optional[str] = None


class StoreCreate(StoreBase):
    pass


class StoreUpdate(StoreBase):
    name: Optional[str] = None


class StoreRead(StoreBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    products: List[ProductRead] = []

    class Config:
        from_attributes = True
