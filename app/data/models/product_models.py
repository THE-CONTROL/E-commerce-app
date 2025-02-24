from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.data.utils.database import Base


class ProductImage(Base):
    __tablename__ = 'product_images'
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    product = relationship('Product')
    url = Column(String)
    is_primary = Column(Boolean, default=False)
    order = Column(String, default=0)

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    code = Column(String)
    condition = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User')
    images = relationship('ProductImage')
    prices = Column(Numeric)
    state = Column(String)
    lga = Column(String)
