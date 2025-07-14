"""Task repository for task-specific database operations."""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, desc

from .base_repository import BaseRepository
from ..models.task import Task
from ..core.logger import get_logger

logger = get_logger(__name__)


class TaskRepository(BaseRepository[Task]):
    """Repository for task-specific database operations."""
    
    def __init__(self, db_session: AsyncSession):
        """Initialize the task repository."""
        super().__init__(db_session, Task)
    
    async def get_by_name(self, name: str) -> Optional[Task]:
        """Get a task by name."""
        return await self.get_by_field("name", name)
    
    async def get_by_difficulty(self, difficulty: str, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks by difficulty level."""
        return await self.get_all(skip=skip, limit=limit, filters={"difficulty": difficulty})
    
    async def get_by_category(self, category: str, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks by category."""
        return await self.get_all(skip=skip, limit=limit, filters={"category": category})
    
    async def get_active_tasks(self, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all active tasks."""
        return await self.get_all(skip=skip, limit=limit, filters={"is_active": True})
    
    async def get_by_environment(self, environment: str, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks by environment."""
        return await self.get_all(skip=skip, limit=limit, filters={"environment": environment})
    
    async def get_tasks_by_difficulty_and_category(
        self, 
        difficulty: str, 
        category: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Task]:
        """Get tasks by difficulty and category."""
        return await self.get_all(
            skip=skip, 
            limit=limit, 
            filters={"difficulty": difficulty, "category": category}
        )
    
    async def get_popular_tasks(self, limit: int = 10) -> List[Task]:
        """Get most popular tasks (this would typically be based on submission count)."""
        try:
            # For now, return active tasks ordered by ID
            # In a real implementation, this would join with submissions table
            result = await self.db.execute(
                select(Task)
                .filter(Task.is_active == True)
                .order_by(desc(Task.id))
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching popular tasks: {e}")
            raise
    
    async def activate_task(self, task_id: int) -> Task:
        """Activate a task."""
        return await self.update(task_id, {"is_active": True})
    
    async def deactivate_task(self, task_id: int) -> Task:
        """Deactivate a task."""
        return await self.update(task_id, {"is_active": False})
    
    async def get_task_with_submissions(self, task_id: int) -> Optional[Task]:
        """Get task with all its submissions."""
        return await self.get_with_relations(task_id, ["submissions"])
    
    async def search_tasks(self, query: str, skip: int = 0, limit: int = 100) -> List[Task]:
        """Search tasks by name or description."""
        try:
            result = await self.db.execute(
                select(Task).filter(
                    or_(
                        Task.name.ilike(f"%{query}%"),
                        Task.description.ilike(f"%{query}%")
                    )
                ).offset(skip).limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error searching tasks: {e}")
            raise
    
    async def get_task_statistics(self, task_id: int) -> dict:
        """Get comprehensive statistics for a task."""
        try:
            task = await self.get_by_id_or_404(task_id)
            
            # Basic stats - in a real implementation, this would involve
            # complex queries with joins to submissions, evaluations, etc.
            stats = {
                "task_id": task.id,
                "name": task.name,
                "difficulty": task.difficulty,
                "category": task.category,
                "environment": task.environment,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "is_active": task.is_active,
                # Additional stats would be calculated here
                "total_submissions": 0,  # To be calculated
                "successful_submissions": 0,  # To be calculated
                "average_score": 0.0,  # To be calculated
                "completion_rate": 0.0,  # To be calculated
            }
            
            return stats
        except Exception as e:
            logger.error(f"Error fetching task statistics for task {task_id}: {e}")
            raise
    
    async def get_tasks_by_complexity_range(
        self, 
        min_complexity: float, 
        max_complexity: float, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Task]:
        """Get tasks within a complexity range."""
        try:
            result = await self.db.execute(
                select(Task).filter(
                    and_(
                        Task.complexity_score >= min_complexity,
                        Task.complexity_score <= max_complexity
                    )
                ).offset(skip).limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching tasks by complexity range: {e}")
            raise