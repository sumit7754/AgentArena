from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.task import Task
from ..models.enums import TaskDifficulty
import uuid

class TaskService:
    def __init__(self, db: Session):
        self._db = db
    
    def create_task(self, task_data: dict, creator_id: uuid.UUID | str) -> Task:
        """Create Task while supporting the simplified payload used in tests."""

        try:
            data = dict(task_data)

            # Map legacy aliases ➜ canonical columns
            if "category" in data and data.get("category") is not None:
                data["webArenaEnvironment"] = data.pop("category")

            if "task_config" in data and data.get("task_config") is not None:
                data["environmentConfig"] = data.pop("task_config")

            data.setdefault("environmentConfig", {})

            # Ensure difficulty is uppercase (enum values are upper-case)
            if "difficulty" in data and isinstance(data["difficulty"], str):
                data["difficulty"] = data["difficulty"].upper()

            # Strip fields that are not model columns
            allowed_columns = {c.name for c in Task.__table__.columns}
            filtered = {k: v for k, v in data.items() if k in allowed_columns}

            filtered["createdBy"] = str(creator_id)

            task = Task(**filtered)
            self._db.add(task)
            self._db.commit()
            self._db.refresh(task)
            return task
        except Exception as e:
            self._db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def get_tasks(self, skip: int = 0, limit: int = 10) -> List[Task]:
        return self._db.query(Task).offset(skip).limit(limit).all()

    def get_task_by_id(self, task_id: uuid.UUID | str) -> Task:
        task = self._db.query(Task).filter(Task.id == str(task_id)).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    def update_task(self, task_id: uuid.UUID | str, task_data: dict) -> Task:
        task = self.get_task_by_id(str(task_id))
        for key, value in task_data.items():
            if value is not None:
                setattr(task, key, value)
        self._db.commit()
        self._db.refresh(task)
        return task
    
    def delete_task(self, task_id: uuid.UUID | str) -> None:
        task = self.get_task_by_id(str(task_id))
        self._db.delete(task)
        self._db.commit()