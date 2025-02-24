from sqlalchemy import Boolean, Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.data.utils.database import Base


class Subscription(Base):
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    duration = Column(String)
    duration_type = Column(String)

class Store(Base):
    __tablename__ = 'stores'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String)
    image = Column(String)
    user = relationship('User')
    description = Column(String)
    subscription = relationship('StoreSubscription', uselist=False, back_populates='store')

class StoreSubscription(Base):
    __tablename__ = 'store_subscriptions'
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey('stores.id'), unique=True, nullable=False)
    subscription_id = Column(Integer)
    store = relationship('Store', back_populates='subscription')
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
