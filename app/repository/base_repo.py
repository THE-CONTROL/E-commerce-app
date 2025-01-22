from sqlalchemy.orm import Session
from typing import Generic, TypeVar, Type, Optional, Any, Dict
from sqlalchemy.orm import Session
from pydantic import BaseModel

        
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType]):
    def __init__(self, model: Type[ModelType], session: Session):
        self.model = model
        self.session = session

    def get_by_field(self, field: str, value: Any) -> Optional[ModelType]:
        """
        Generic method to get an entity by any field
        """
        return self.session.query(self.model).filter(getattr(self.model, field) == value).first()

    def create(self, data: Dict[str, Any]) -> Dict:
        """
        Create a new record from a dictionary of data
        """
        new_instance = self.model(**data)
        self.session.add(instance=new_instance)
        self.session.commit()
        self.session.refresh(new_instance)
        return {"id": new_instance.id}

    def update(self, instance: Any) -> Dict[str, Any]:
        """Update an existing record"""
        try:
            self.session.add(instance)
            self.session.commit()
            self.session.refresh(instance)
            
            # Return a dictionary representation
            return instance
        except Exception as e:
            self.session.rollback()
            raise e

    def delete(self, db_obj: ModelType) -> None:
        """
        Generic delete method
        """
        self.session.delete(db_obj)
        self.session.commit()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """
        Generic method to get all records with pagination
        """
        return self.session.query(self.model).offset(skip).limit(limit).all()
