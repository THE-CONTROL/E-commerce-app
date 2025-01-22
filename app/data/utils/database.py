from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from typing import Generator
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database URL configuration
POSTGRES_DATABASE_URL: str = os.getenv("POSTGRES_DATABASE_URL")

# Create engine
engine = create_engine(POSTGRES_DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create declarative base for models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Database dependency that handles session lifecycle
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
