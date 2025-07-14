"""Base repository class with common database operations."""

from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func, and_, or_
from abc import ABC, abstractmethod

from ..core.exceptions import DatabaseException, NotFoundException
from ..core.logger import get_logger

logger = get_logger(__name__)

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType], ABC):
    """Base repository class with common database operations."""
    
    def __init__(self, db_session: AsyncSession, model: Type[ModelType]):
        """Initialize the repository with a database session and model."""
        self.db = db_session
        self.model = model
    
    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get a record by ID."""
        try:
            result = await self.db.execute(select(self.model).filter(self.model.id == id))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching {self.model.__name__} by ID {id}: {e}")
            raise DatabaseException(f"Failed to fetch {self.model.__name__} by ID")
    
    async def get_by_id_or_404(self, id: int) -> ModelType:
        """Get a record by ID or raise 404 error."""
        record = await self.get_by_id(id)
        if not record:
            raise NotFoundException(
                f"{self.model.__name__} not found",
                resource_type=self.model.__name__,
                resource_id=str(id)
            )
        return record
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        order_by: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Get all records with optional pagination and filtering."""
        try:
            query = select(self.model)
            
            # Apply filters
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        query = query.filter(getattr(self.model, key) == value)
            
            # Apply ordering
            if order_by and hasattr(self.model, order_by):
                query = query.order_by(getattr(self.model, order_by))
            
            # Apply pagination
            query = query.offset(skip).limit(limit)
            
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching all {self.model.__name__}: {e}")
            raise DatabaseException(f"Failed to fetch {self.model.__name__} records")
    
    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """Create a new record."""
        try:
            db_obj = self.model(**obj_in)
            self.db.add(db_obj)
            await self.db.commit()
            await self.db.refresh(db_obj)
            logger.info(f"Created {self.model.__name__} with ID: {db_obj.id}")
            return db_obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating {self.model.__name__}: {e}")
            raise DatabaseException(f"Failed to create {self.model.__name__}")
    
    async def update(self, id: int, obj_in: Dict[str, Any]) -> ModelType:
        """Update a record by ID."""
        try:
            db_obj = await self.get_by_id_or_404(id)
            
            for key, value in obj_in.items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)
            
            await self.db.commit()
            await self.db.refresh(db_obj)
            logger.info(f"Updated {self.model.__name__} with ID: {id}")
            return db_obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating {self.model.__name__} with ID {id}: {e}")
            raise DatabaseException(f"Failed to update {self.model.__name__}")
    
    async def delete(self, id: int) -> bool:
        """Delete a record by ID."""
        try:
            db_obj = await self.get_by_id_or_404(id)
            await self.db.delete(db_obj)
            await self.db.commit()
            logger.info(f"Deleted {self.model.__name__} with ID: {id}")
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting {self.model.__name__} with ID {id}: {e}")
            raise DatabaseException(f"Failed to delete {self.model.__name__}")
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filtering."""
        try:
            query = select(func.count(self.model.id))
            
            # Apply filters
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        query = query.filter(getattr(self.model, key) == value)
            
            result = await self.db.execute(query)
            return result.scalar()
        except Exception as e:
            logger.error(f"Error counting {self.model.__name__}: {e}")
            raise DatabaseException(f"Failed to count {self.model.__name__} records")
    
    async def exists(self, id: int) -> bool:
        """Check if a record exists by ID."""
        try:
            result = await self.db.execute(
                select(func.count(self.model.id)).filter(self.model.id == id)
            )
            return result.scalar() > 0
        except Exception as e:
            logger.error(f"Error checking existence of {self.model.__name__} with ID {id}: {e}")
            raise DatabaseException(f"Failed to check existence of {self.model.__name__}")
    
    async def get_by_field(self, field: str, value: Any) -> Optional[ModelType]:
        """Get a record by a specific field."""
        try:
            if not hasattr(self.model, field):
                raise ValueError(f"Field '{field}' not found in {self.model.__name__}")
            
            result = await self.db.execute(
                select(self.model).filter(getattr(self.model, field) == value)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching {self.model.__name__} by {field}: {e}")
            raise DatabaseException(f"Failed to fetch {self.model.__name__} by {field}")
    
    async def get_many_by_field(self, field: str, value: Any) -> List[ModelType]:
        """Get multiple records by a specific field."""
        try:
            if not hasattr(self.model, field):
                raise ValueError(f"Field '{field}' not found in {self.model.__name__}")
            
            result = await self.db.execute(
                select(self.model).filter(getattr(self.model, field) == value)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching {self.model.__name__} by {field}: {e}")
            raise DatabaseException(f"Failed to fetch {self.model.__name__} by {field}")
    
    async def bulk_create(self, objects: List[Dict[str, Any]]) -> List[ModelType]:
        """Create multiple records at once."""
        try:
            db_objs = [self.model(**obj) for obj in objects]
            self.db.add_all(db_objs)
            await self.db.commit()
            
            # Refresh all objects
            for db_obj in db_objs:
                await self.db.refresh(db_obj)
            
            logger.info(f"Created {len(db_objs)} {self.model.__name__} records")
            return db_objs
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error bulk creating {self.model.__name__}: {e}")
            raise DatabaseException(f"Failed to bulk create {self.model.__name__}")
    
    async def get_with_relations(self, id: int, relations: List[str]) -> Optional[ModelType]:
        """Get a record with eager loading of specified relations."""
        try:
            query = select(self.model).filter(self.model.id == id)
            
            # Add eager loading for specified relations
            for relation in relations:
                if hasattr(self.model, relation):
                    query = query.options(selectinload(getattr(self.model, relation)))
            
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching {self.model.__name__} with relations: {e}")
            raise DatabaseException(f"Failed to fetch {self.model.__name__} with relations")