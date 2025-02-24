from decimal import Decimal
from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import Optional, List
from enum import Enum


class ProductCondition(str, Enum):
    NEW = "new"
    USED = "used"
    REFURBISHED = "refurbished"


class ProductImageBase(BaseModel):
    url: HttpUrl
    is_primary: bool = False
    order: int = Field(default=0, ge=0)


class ProductImageCreate(ProductImageBase):
    pass


class ProductImageRead(ProductImageBase):
    id: int
    product_id: int

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    code: Optional[str] = None
    condition: ProductCondition
    prices: Decimal = Field(
        ...,
        gt=Decimal(0),
        description="Product price with 2 decimal places"
    )
    state: str = Field(..., min_length=2, max_length=100)
    lga: str = Field(..., min_length=2, max_length=100)

    @field_validator('prices')
    @classmethod
    def validate_price(cls, v: Decimal) -> Decimal:
        # Ensure price has max 10 digits with exactly 2 decimal places
        if v.quantize(Decimal('.01')) != v:
            raise ValueError('Price must have exactly 2 decimal places')
        if len(str(v)) > 13:  # 10 digits + decimal point + 2 decimal places
            raise ValueError('Price must not exceed 10 digits before decimal point')
        return v


class ProductCreate(ProductBase):
    images: List[ProductImageCreate] = Field(..., min_length=1)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    code: Optional[str] = None
    condition: Optional[ProductCondition] = None
    prices: Optional[Decimal] = Field(
        None,
        gt=Decimal(0),
        description="Product price with 2 decimal places"
    )
    state: Optional[str] = Field(None, min_length=2, max_length=100)
    lga: Optional[str] = Field(None, min_length=2, max_length=100)
    images: Optional[List[ProductImageCreate]] = None

    @field_validator('prices')
    @classmethod
    def validate_update_price(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is None:
            return v
        # Ensure price has max 10 digits with exactly 2 decimal places
        if v.quantize(Decimal('.01')) != v:
            raise ValueError('Price must have exactly 2 decimal places')
        if len(str(v)) > 13:  # 10 digits + decimal point + 2 decimal places
            raise ValueError('Price must not exceed 10 digits before decimal point')
        return v


class ProductRead(ProductBase):
    id: int
    user_id: int
    images: List[ProductImageRead]

    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    message: str
    data: ProductRead


class ProductListResponse(BaseModel):
    message: str
    data: List[ProductRead]
    total: int
    page: int
    size: int