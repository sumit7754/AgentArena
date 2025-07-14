from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from ...db.database import get_db
from ...controllers.task_controller import TaskController
from ...controllers.submission_controller import SubmissionController
from ...schemas.task_schema import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from ...schemas.submission_schema import LeaderboardResponse
from ...core.security import get_current_user
import uuid

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("", status_code=201)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    controller = TaskController(db)
    return await controller.create_task(task, current_user.id)

@router.get("", status_code=200)
async def get_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    controller = TaskController(db)
    result = await controller.get_tasks(skip, limit)
    return result

@router.get("/{task_id}")
async def get_task(
    task_id: str,
    db: Session = Depends(get_db),
):
    controller = TaskController(db)
    return await controller.get_task(task_id)

@router.get("/{task_id}/leaderboard", response_model=list[LeaderboardResponse])
async def get_task_leaderboard(
    task_id: str,
    db: Session = Depends(get_db),
):
    try:
        task_uuid = uuid.UUID(task_id)
        controller = SubmissionController(db)
        return await controller.get_leaderboard(task_uuid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID format")

@router.put("/{task_id}")
async def update_task(
    task_id: str,
    task: TaskUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    controller = TaskController(db)
    return await controller.update_task(task_id, task)

@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    controller = TaskController(db)
    await controller.delete_task(task_id)
    return {"message": "Task deleted successfully"}