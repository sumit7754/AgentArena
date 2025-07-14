"""Evaluation repository for evaluation-specific database operations."""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, desc, func

from .base_repository import BaseRepository
from ..models.evaluation import EvaluationResult
from ..core.logger import get_logger

logger = get_logger(__name__)


class EvaluationRepository(BaseRepository[EvaluationResult]):
    """Repository for evaluation-specific database operations."""
    
    def __init__(self, db_session: AsyncSession):
        """Initialize the evaluation repository."""
        super().__init__(db_session, EvaluationResult)
    
    async def get_by_submission_id(self, submission_id: int) -> Optional[EvaluationResult]:
        """Get evaluation by submission ID."""
        return await self.get_by_field("submission_id", submission_id)
    
    async def get_by_task_id(self, task_id: int, skip: int = 0, limit: int = 100) -> List[EvaluationResult]:
        """Get all evaluations for a specific task."""
        return await self.get_many_by_field("task_id", task_id)
    
    async def get_by_agent_id(self, agent_id: int, skip: int = 0, limit: int = 100) -> List[EvaluationResult]:
        """Get all evaluations for a specific agent."""
        return await self.get_many_by_field("agent_id", agent_id)
    
    async def get_successful_evaluations(self, skip: int = 0, limit: int = 100) -> List[EvaluationResult]:
        """Get all successful evaluations."""
        return await self.get_all(skip=skip, limit=limit, filters={"task_completed": True})
    
    async def get_failed_evaluations(self, skip: int = 0, limit: int = 100) -> List[EvaluationResult]:
        """Get all failed evaluations."""
        return await self.get_all(skip=skip, limit=limit, filters={"task_completed": False})
    
    async def get_evaluations_by_score_range(
        self, 
        min_score: float, 
        max_score: float, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[EvaluationResult]:
        """Get evaluations within a score range."""
        try:
            result = await self.db.execute(
                select(EvaluationResult).filter(
                    and_(
                        EvaluationResult.total_score >= min_score,
                        EvaluationResult.total_score <= max_score
                    )
                ).offset(skip).limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching evaluations by score range: {e}")
            raise
    
    async def get_top_evaluations_by_task(self, task_id: int, limit: int = 10) -> List[EvaluationResult]:
        """Get top evaluations for a specific task."""
        try:
            result = await self.db.execute(
                select(EvaluationResult).filter(
                    EvaluationResult.task_id == task_id
                ).order_by(desc(EvaluationResult.total_score)).limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching top evaluations for task {task_id}: {e}")
            raise
    
    async def get_evaluation_with_submission(self, evaluation_id: int) -> Optional[EvaluationResult]:
        """Get evaluation with its submission."""
        return await self.get_with_relations(evaluation_id, ["submission"])
    
    async def get_task_completion_rate(self, task_id: int) -> float:
        """Get completion rate for a specific task."""
        try:
            # Count total evaluations for task
            total_result = await self.db.execute(
                select(func.count(EvaluationResult.id)).filter(
                    EvaluationResult.task_id == task_id
                )
            )
            total_evaluations = total_result.scalar() or 0
            
            # Count successful evaluations for task
            success_result = await self.db.execute(
                select(func.count(EvaluationResult.id)).filter(
                    and_(
                        EvaluationResult.task_id == task_id,
                        EvaluationResult.task_completed == True
                    )
                )
            )
            successful_evaluations = success_result.scalar() or 0
            
            return successful_evaluations / total_evaluations if total_evaluations > 0 else 0.0
        except Exception as e:
            logger.error(f"Error calculating completion rate for task {task_id}: {e}")
            raise
    
    async def get_agent_performance_metrics(self, agent_id: int) -> dict:
        """Get performance metrics for an agent."""
        try:
            # Count total evaluations for agent
            total_result = await self.db.execute(
                select(func.count(EvaluationResult.id)).filter(
                    EvaluationResult.agent_id == agent_id
                )
            )
            total_evaluations = total_result.scalar() or 0
            
            # Count successful evaluations for agent
            success_result = await self.db.execute(
                select(func.count(EvaluationResult.id)).filter(
                    and_(
                        EvaluationResult.agent_id == agent_id,
                        EvaluationResult.task_completed == True
                    )
                )
            )
            successful_evaluations = success_result.scalar() or 0
            
            # Calculate average score
            avg_score_result = await self.db.execute(
                select(func.avg(EvaluationResult.total_score)).filter(
                    EvaluationResult.agent_id == agent_id
                )
            )
            avg_score = avg_score_result.scalar() or 0.0
            
            # Calculate average execution time
            avg_time_result = await self.db.execute(
                select(func.avg(EvaluationResult.execution_time)).filter(
                    EvaluationResult.agent_id == agent_id
                )
            )
            avg_execution_time = avg_time_result.scalar() or 0.0
            
            return {
                "agent_id": agent_id,
                "total_evaluations": total_evaluations,
                "successful_evaluations": successful_evaluations,
                "success_rate": successful_evaluations / total_evaluations if total_evaluations > 0 else 0.0,
                "average_score": float(avg_score),
                "average_execution_time": float(avg_execution_time),
            }
        except Exception as e:
            logger.error(f"Error fetching agent performance metrics: {e}")
            raise
    
    async def get_evaluation_statistics(self, evaluation_id: int) -> dict:
        """Get comprehensive statistics for an evaluation."""
        try:
            evaluation = await self.get_by_id_or_404(evaluation_id)
            
            stats = {
                "evaluation_id": evaluation.id,
                "submission_id": evaluation.submission_id,
                "task_id": evaluation.task_id,
                "agent_id": evaluation.agent_id,
                "task_completed": evaluation.task_completed,
                "total_score": evaluation.total_score,
                "execution_time": evaluation.execution_time,
                "steps_taken": evaluation.steps_taken,
                "created_at": evaluation.created_at,
                "updated_at": evaluation.updated_at,
                # Additional metrics would be calculated here
            }
            
            return stats
        except Exception as e:
            logger.error(f"Error fetching evaluation statistics for evaluation {evaluation_id}: {e}")
            raise
    
    async def get_task_performance_summary(self, task_id: int) -> dict:
        """Get performance summary for a specific task."""
        try:
            # Count total evaluations
            total_result = await self.db.execute(
                select(func.count(EvaluationResult.id)).filter(
                    EvaluationResult.task_id == task_id
                )
            )
            total_evaluations = total_result.scalar() or 0
            
            # Count successful evaluations
            success_result = await self.db.execute(
                select(func.count(EvaluationResult.id)).filter(
                    and_(
                        EvaluationResult.task_id == task_id,
                        EvaluationResult.task_completed == True
                    )
                )
            )
            successful_evaluations = success_result.scalar() or 0
            
            # Calculate average score
            avg_score_result = await self.db.execute(
                select(func.avg(EvaluationResult.total_score)).filter(
                    EvaluationResult.task_id == task_id
                )
            )
            avg_score = avg_score_result.scalar() or 0.0
            
            # Get highest score
            max_score_result = await self.db.execute(
                select(func.max(EvaluationResult.total_score)).filter(
                    EvaluationResult.task_id == task_id
                )
            )
            max_score = max_score_result.scalar() or 0.0
            
            return {
                "task_id": task_id,
                "total_evaluations": total_evaluations,
                "successful_evaluations": successful_evaluations,
                "completion_rate": successful_evaluations / total_evaluations if total_evaluations > 0 else 0.0,
                "average_score": float(avg_score),
                "highest_score": float(max_score),
            }
        except Exception as e:
            logger.error(f"Error fetching task performance summary: {e}")
            raise