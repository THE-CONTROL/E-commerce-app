from decimal import Decimal
from pydantic import BaseModel, condecimal
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal = condecimal(max_digits=10, decimal_places=2)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = condecimal(max_digits=10, decimal_places=2)


class ProductRead(ProductBase):
    id: int
    store_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
