from sqlalchemy import TIMESTAMP, Boolean, Column, Integer, String, ForeignKey, text, Numeric
from sqlalchemy.orm import relationship
from app.data.utils.database import Base
from datetime import datetime, timezone


class Store(Base):
    __tablename__ = "stores"
    __table_args__ = {'comment': 'Stores information about user stores'}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
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
    user = relationship("User", back_populates="stores")
    products = relationship("Product", back_populates="store", cascade="all, delete-orphan")
