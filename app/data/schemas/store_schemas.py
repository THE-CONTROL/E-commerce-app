from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.core.constants import DurationType, SubscriptionType

class SubscriptionBase(BaseModel):
    name: str
    description: str
    features: List[str]
    monthly_amount: float
    yearly_amount: float

class SubscriptionRead(SubscriptionBase):
    id: int
    type: SubscriptionType
    features: List[str]

    class Config:
        from_attributes = True

class StoreBase(BaseModel):
    name: str
    description: Optional[str] = None
    image: Optional[str] = None

class StoreCreate(StoreBase):
    subscription_id: int
    duration_type: DurationType = DurationType.MONTHLY

class StoreUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    duration_type: Optional[DurationType] = None

class StoreSubscriptionRead(BaseModel):
    id: int
    store_id: int
    subscription_id: Optional[int]  # Make this optional if needed
    start_date: datetime
    end_date: datetime
    is_active: bool

    class Config:
        from_attributes = True

class StoreRead(StoreBase):
    id: int
    user_id: int
    subscription: Optional[StoreSubscriptionRead] = None

    class Config:
        from_attributes = True