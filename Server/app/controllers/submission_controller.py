from fastapi import HTTPException
from ..services.submission_service import SubmissionService
from ..schemas.submission_schema import SubmissionCreate, SubmissionResponse, SubmissionListResponse, EvaluationResultResponse, LeaderboardResponse, PlaygroundDetailsResponse
from ..models.enums import SubmissionStatus, EvaluationStatus
from sqlalchemy.orm import Session
import uuid
from fastapi import BackgroundTasks
import asyncio
from datetime import datetime
from ..core.exceptions import NotFoundException

class SubmissionController:
    def __init__(self, db: Session):
        self.submission_service = SubmissionService(db)

    async def create_submission(self, submission_data: SubmissionCreate, user_id: uuid.UUID, background_tasks: BackgroundTasks) -> SubmissionResponse:
        try:
            # Accept both camelCase and snake_case fields
            # Call the async create_submission directly to avoid event-loop issues
            submission = await self.submission_service.create_submission(
                self.submission_service._db,  # type: ignore
                SubmissionCreate(
                    agent_id=submission_data.agentId_resolved,
                    task_id=submission_data.taskId_resolved,
                    run_config=getattr(submission_data, "run_config", {}),
                ),
                user_id,
            )
            # Spawn async processing (mock playground) – fire-and-forget
            background_tasks.add_task(
                self._process_submission_async,
                submission.id,
                submission_data.taskId_resolved,
            )
            return self._format_submission_response(submission)
        except NotFoundException as nf:
            # Let global exception handler format the 404 response
            raise nf
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def _process_submission_async(self, submission_id: uuid.UUID, task_id: uuid.UUID):
        """
        Wrapper method to handle async WebArena evaluation in background tasks.
        """
        try:
            await self.submission_service.process_submission(submission_id, task_id)
        except Exception as e:
            # Log the error but don't raise it since this is a background task
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Background WebArena evaluation failed for submission {submission_id}: {e}")

    async def get_user_submissions(self, user_id: uuid.UUID, skip: int = 0, limit: int = 20):
        result = self.submission_service.get_user_submissions(user_id, skip, limit)
        return {
            "items": [self._format_submission_response(sub) for sub in result["items"]],
            "total": result["total"],
        }
    
    async def get_submission_details(self, submission_id: uuid.UUID, user_id: uuid.UUID) -> SubmissionResponse:
        try:
            submission = self.submission_service._get_full_submission(submission_id)
            if not submission:
                raise HTTPException(status_code=404, detail="Submission not found")
            if submission.userId != user_id:
                raise HTTPException(status_code=403, detail="You do not have permission to access this submission")
            return self._format_submission_response(submission)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    
    def _format_submission_response(self, submission):
        """Return a plain dict that matches the simplified schema expected by
        the automated tests (flat keys, no nested `playgroundDetails`)."""

        return {
            "id": submission.id,
            "agent_id": submission.agentId,
            "task_id": submission.taskId,
            "status": submission.status,
            "submitted_at": submission.submittedAt,
            "playground_execution_id": submission.playground_execution_id,
            "steps_taken": submission.steps_taken,
            "execution_time_seconds": submission.execution_time_seconds,
            "success_rate": submission.success_rate,
            "result_data": submission.result_data,
        }
    
    async def get_leaderboard(self, task_id: uuid.UUID) -> list[LeaderboardResponse]:
        try:
            leaderboard_entries = self.submission_service.get_leaderboard(task_id)
            return leaderboard_entries
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_user_submissions_by_task(self,userId:uuid.UUID,taskId:uuid.UUID,skip:int=0 , limit : int = 20) -> SubmissionListResponse :
        result = self.submission_service.get_user_submissions_by_task(userId,taskId, skip, limit)
        return {
            "items": [self._format_submission_response(sub) for sub in result["items"]],
            "total": result["total"],
        }
        