from sqlalchemy import TIMESTAMP, Boolean, Column, Integer, String, ForeignKey, text, Numeric
from sqlalchemy.orm import relationship
from app.data.utils.database import Base
from datetime import datetime, timezone


class Product(Base):
    __tablename__ = "products"
    __table_args__ = {'comment': 'Stores product information'}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    price = Column(Numeric(10, 2), nullable=False)
    store_id = Column(Integer, ForeignKey('stores.id'), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text('now()'),
        nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text('now()'),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    store = relationship("Store", back_populates="products")