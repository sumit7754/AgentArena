from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from ...db.database import get_db
from fastapi import BackgroundTasks
from ...controllers.submission_controller import SubmissionController
from ...schemas.submission_schema import (
    SubmissionCreate, 
    SubmissionResponse, 
    SubmissionListResponse,
    LeaderboardResponse
)
from ...core.security import get_current_user
import uuid

router = APIRouter(prefix="/submissions", tags=["Submissions"])

@router.post("", status_code=201)
async def submit_agent(
    submission: SubmissionCreate,
    background_tasks: BackgroundTasks,  
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    controller = SubmissionController(db)
    return await controller.create_submission(submission, current_user.id, background_tasks)  

@router.get("/my", response_model=SubmissionListResponse)
async def get_my_submissions_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    controller = SubmissionController(db)
    return await controller.get_user_submissions(
        current_user.id,
        skip=skip,
        limit=limit
    )

@router.get("")
async def get_my_submissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    controller = SubmissionController(db)
    return await controller.get_user_submissions(
        current_user.id,
        skip=skip,
        limit=limit
    )

@router.get("/{submission_id}")
async def get_submission(
    submission_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        submission_uuid = uuid.UUID(submission_id)
        controller = SubmissionController(db)
        return await controller.get_submission_details(submission_uuid, current_user.id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid submission ID format")

@router.get("/leaderboard/{task_id}", response_model=list[LeaderboardResponse])
async def get_leaderboard(
    task_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        task_uuid = uuid.UUID(task_id)
        controller = SubmissionController(db)
        return await controller.get_leaderboard(task_uuid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID format")

@router.get("/task/{task_id}", response_model=SubmissionListResponse)
async def get_my_submissions_by_task(
    task_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        task_uuid = uuid.UUID(task_id)
        controller = SubmissionController(db)
        return await controller.get_user_submissions_by_task(
            current_user.id, task_uuid, skip=skip, limit=limit
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID format")