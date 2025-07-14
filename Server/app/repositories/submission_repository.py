"""Submission repository for submission-specific database operations."""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, desc, func
from datetime import datetime, timedelta

from .base_repository import BaseRepository
from ..models.submission import Submission
from ..core.logger import get_logger

logger = get_logger(__name__)


class SubmissionRepository(BaseRepository[Submission]):
    """Repository for submission-specific database operations."""
    
    def __init__(self, db_session: AsyncSession):
        """Initialize the submission repository."""
        super().__init__(db_session, Submission)
    
    async def get_by_agent_id(self, agent_id: int, skip: int = 0, limit: int = 100) -> List[Submission]:
        """Get all submissions for a specific agent."""
        return await self.get_many_by_field("agent_id", agent_id)
    
    async def get_by_task_id(self, task_id: int, skip: int = 0, limit: int = 100) -> List[Submission]:
        """Get all submissions for a specific task."""
        return await self.get_many_by_field("task_id", task_id)
    
    async def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Submission]:
        """Get all submissions for a specific user."""
        return await self.get_many_by_field("user_id", user_id)
    
    async def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Submission]:
        """Get all submissions by status."""
        return await self.get_all(skip=skip, limit=limit, filters={"status": status})
    
    async def get_by_agent_and_task(self, agent_id: int, task_id: int) -> List[Submission]:
        """Get all submissions for a specific agent and task combination."""
        try:
            result = await self.db.execute(
                select(Submission).filter(
                    and_(
                        Submission.agent_id == agent_id,
                        Submission.task_id == task_id
                    )
                )
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching submissions by agent and task: {e}")
            raise
    
    async def get_latest_submission_by_agent_and_task(
        self, 
        agent_id: int, 
        task_id: int
    ) -> Optional[Submission]:
        """Get the latest submission for a specific agent and task."""
        try:
            result = await self.db.execute(
                select(Submission).filter(
                    and_(
                        Submission.agent_id == agent_id,
                        Submission.task_id == task_id
                    )
                ).order_by(desc(Submission.created_at)).limit(1)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching latest submission: {e}")
            raise
    
    async def get_successful_submissions(self, skip: int = 0, limit: int = 100) -> List[Submission]:
        """Get all successful submissions."""
        return await self.get_all(skip=skip, limit=limit, filters={"status": "completed"})
    
    async def get_failed_submissions(self, skip: int = 0, limit: int = 100) -> List[Submission]:
        """Get all failed submissions."""
        return await self.get_all(skip=skip, limit=limit, filters={"status": "failed"})
    
    async def get_pending_submissions(self, skip: int = 0, limit: int = 100) -> List[Submission]:
        """Get all pending submissions."""
        return await self.get_all(skip=skip, limit=limit, filters={"status": "pending"})
    
    async def get_submissions_by_score_range(
        self, 
        min_score: float, 
        max_score: float, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Submission]:
        """Get submissions within a score range."""
        try:
            result = await self.db.execute(
                select(Submission).filter(
                    and_(
                        Submission.score >= min_score,
                        Submission.score <= max_score
                    )
                ).offset(skip).limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching submissions by score range: {e}")
            raise
    
    async def get_top_submissions_by_task(self, task_id: int, limit: int = 10) -> List[Submission]:
        """Get top submissions for a specific task."""
        try:
            result = await self.db.execute(
                select(Submission).filter(
                    and_(
                        Submission.task_id == task_id,
                        Submission.status == "completed"
                    )
                ).order_by(desc(Submission.score)).limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching top submissions for task {task_id}: {e}")
            raise
    
    async def get_recent_submissions(self, hours: int = 24, skip: int = 0, limit: int = 100) -> List[Submission]:
        """Get recent submissions within specified hours."""
        try:
            since = datetime.utcnow() - timedelta(hours=hours)
            result = await self.db.execute(
                select(Submission).filter(
                    Submission.created_at >= since
                ).order_by(desc(Submission.created_at)).offset(skip).limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching recent submissions: {e}")
            raise
    
    async def get_submission_with_evaluation(self, submission_id: int) -> Optional[Submission]:
        """Get submission with its evaluation results."""
        return await self.get_with_relations(submission_id, ["evaluations"])
    
    async def update_submission_status(self, submission_id: int, status: str) -> Submission:
        """Update the status of a submission."""
        return await self.update(submission_id, {"status": status})
    
    async def update_submission_score(self, submission_id: int, score: float) -> Submission:
        """Update the score of a submission."""
        return await self.update(submission_id, {"score": score})
    
    async def get_submission_statistics(self, submission_id: int) -> dict:
        """Get comprehensive statistics for a submission."""
        try:
            submission = await self.get_by_id_or_404(submission_id)
            
            stats = {
                "submission_id": submission.id,
                "agent_id": submission.agent_id,
                "task_id": submission.task_id,
                "user_id": submission.user_id,
                "status": submission.status,
                "score": submission.score,
                "created_at": submission.created_at,
                "updated_at": submission.updated_at,
                "execution_time": submission.execution_time,
                "steps_taken": submission.steps_taken,
                # Additional stats would be calculated here
            }
            
            return stats
        except Exception as e:
            logger.error(f"Error fetching submission statistics for submission {submission_id}: {e}")
            raise
    
    async def get_agent_performance_summary(self, agent_id: int) -> dict:
        """Get performance summary for an agent."""
        try:
            # Count total submissions
            total_result = await self.db.execute(
                select(func.count(Submission.id)).filter(Submission.agent_id == agent_id)
            )
            total_submissions = total_result.scalar() or 0
            
            # Count successful submissions
            success_result = await self.db.execute(
                select(func.count(Submission.id)).filter(
                    and_(
                        Submission.agent_id == agent_id,
                        Submission.status == "completed"
                    )
                )
            )
            successful_submissions = success_result.scalar() or 0
            
            # Calculate average score
            avg_score_result = await self.db.execute(
                select(func.avg(Submission.score)).filter(
                    and_(
                        Submission.agent_id == agent_id,
                        Submission.status == "completed"
                    )
                )
            )
            avg_score = avg_score_result.scalar() or 0.0
            
            return {
                "agent_id": agent_id,
                "total_submissions": total_submissions,
                "successful_submissions": successful_submissions,
                "success_rate": successful_submissions / total_submissions if total_submissions > 0 else 0,
                "average_score": float(avg_score),
            }
        except Exception as e:
            logger.error(f"Error fetching agent performance summary: {e}")
            raise