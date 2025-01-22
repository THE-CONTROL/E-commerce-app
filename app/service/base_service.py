from typing import Any, Generic, TypeVar, Dict
from fastapi import HTTPException, status
from pydantic import BaseModel

from app.repository.base_repo import BaseRepository


ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, repository: BaseRepository):
        self._repository = repository

    def get_by_id(self, id: int) -> ModelType:
        """
        Generic get by id method with error handling
        """
        item = self._repository.get_by_field("id", id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.__class__.__name__.replace('Service', '')} not found."
            )
        return item

    def create(self, data: CreateSchemaType) -> Dict:
        """
        Generic create method
        """
        try:
            return self._repository.create(data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    def update(self, id: int, data: UpdateSchemaType) -> Dict[str, Any]:
        """
        Generic update method with error handling
        """
        try:
            # Get existing item
            item = self.get_by_id(id)
            
            # Convert pydantic model to dict, excluding unset values
            update_data = data.model_dump(exclude_unset=True)
            
            # Update only provided fields
            for key, value in update_data.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            
            # Perform update
            result = self._repository.update(item)
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    def delete(self, id: int) -> None:
        """
        Generic delete method
        """
        item = self.get_by_id(id)  # This will raise 404 if not found
        self._repository.delete(item)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """
        Generic get all method
        """
        return self._repository.get_all(skip=skip, limit=limit)