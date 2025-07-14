"""Leaderboard repository for leaderboard-specific database operations."""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, desc, func, text
from datetime import datetime, timedelta

from .base_repository import BaseRepository
from ..models.leaderboard import LeaderboardEntry
from ..core.logger import get_logger

logger = get_logger(__name__)


class LeaderboardRepository(BaseRepository[LeaderboardEntry]):
    """Repository for leaderboard-specific database operations."""
    
    def __init__(self, db_session: AsyncSession):
        """Initialize the leaderboard repository."""
        super().__init__(db_session, LeaderboardEntry)
    
    async def get_by_task_id(self, task_id: int, skip: int = 0, limit: int = 100) -> List[LeaderboardEntry]:
        """Get all leaderboard entries for a specific task."""
        return await self.get_many_by_field("task_id", task_id)
    
    async def get_by_agent_id(self, agent_id: int, skip: int = 0, limit: int = 100) -> List[LeaderboardEntry]:
        """Get all leaderboard entries for a specific agent."""
        return await self.get_many_by_field("agent_id", agent_id)
    
    async def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> List[LeaderboardEntry]:
        """Get all leaderboard entries for a specific user."""
        return await self.get_many_by_field("user_id", user_id)
    
    async def get_top_entries_by_task(self, task_id: int, limit: int = 10) -> List[LeaderboardEntry]:
        """Get top leaderboard entries for a specific task."""
        try:
            result = await self.db.execute(
                select(LeaderboardEntry).filter(
                    LeaderboardEntry.task_id == task_id
                ).order_by(desc(LeaderboardEntry.score)).limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching top entries for task {task_id}: {e}")
            raise
    
    async def get_global_leaderboard(self, limit: int = 50) -> List[LeaderboardEntry]:
        """Get global leaderboard across all tasks."""
        try:
            result = await self.db.execute(
                select(LeaderboardEntry)
                .order_by(desc(LeaderboardEntry.score))
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching global leaderboard: {e}")
            raise
    
    async def get_agent_rank_in_task(self, agent_id: int, task_id: int) -> Optional[int]:
        """Get the rank of an agent in a specific task."""
        try:
            # Get all entries for the task ordered by score descending
            result = await self.db.execute(
                select(LeaderboardEntry).filter(
                    LeaderboardEntry.task_id == task_id
                ).order_by(desc(LeaderboardEntry.score))
            )
            entries = result.scalars().all()
            
            # Find the rank of the agent
            for rank, entry in enumerate(entries, 1):
                if entry.agent_id == agent_id:
                    return rank
            return None
        except Exception as e:
            logger.error(f"Error fetching agent rank: {e}")
            raise
    
    async def get_user_rank_in_task(self, user_id: int, task_id: int) -> Optional[int]:
        """Get the rank of a user's best agent in a specific task."""
        try:
            # Get the best entry for the user in the task
            result = await self.db.execute(
                select(LeaderboardEntry).filter(
                    and_(
                        LeaderboardEntry.user_id == user_id,
                        LeaderboardEntry.task_id == task_id
                    )
                ).order_by(desc(LeaderboardEntry.score)).limit(1)
            )
            best_entry = result.scalar_one_or_none()
            
            if not best_entry:
                return None
            
            return await self.get_agent_rank_in_task(best_entry.agent_id, task_id)
        except Exception as e:
            logger.error(f"Error fetching user rank: {e}")
            raise
    
    async def get_recent_entries(self, hours: int = 24, skip: int = 0, limit: int = 100) -> List[LeaderboardEntry]:
        """Get recent leaderboard entries."""
        try:
            since = datetime.utcnow() - timedelta(hours=hours)
            result = await self.db.execute(
                select(LeaderboardEntry).filter(
                    LeaderboardEntry.created_at >= since
                ).order_by(desc(LeaderboardEntry.created_at)).offset(skip).limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching recent entries: {e}")
            raise
    
    async def get_leaderboard_stats(self, task_id: Optional[int] = None) -> Dict[str, Any]:
        """Get leaderboard statistics."""
        try:
            query = select(LeaderboardEntry)
            if task_id:
                query = query.filter(LeaderboardEntry.task_id == task_id)
            
            # Count total entries
            total_result = await self.db.execute(
                select(func.count(LeaderboardEntry.id)).select_from(query.subquery())
            )
            total_entries = total_result.scalar() or 0
            
            # Get average score
            avg_score_result = await self.db.execute(
                select(func.avg(LeaderboardEntry.score)).select_from(query.subquery())
            )
            avg_score = avg_score_result.scalar() or 0.0
            
            # Get highest score
            max_score_result = await self.db.execute(
                select(func.max(LeaderboardEntry.score)).select_from(query.subquery())
            )
            max_score = max_score_result.scalar() or 0.0
            
            # Get lowest score
            min_score_result = await self.db.execute(
                select(func.min(LeaderboardEntry.score)).select_from(query.subquery())
            )
            min_score = min_score_result.scalar() or 0.0
            
            stats = {
                "total_entries": total_entries,
                "average_score": float(avg_score),
                "highest_score": float(max_score),
                "lowest_score": float(min_score),
            }
            
            if task_id:
                stats["task_id"] = task_id
            
            return stats
        except Exception as e:
            logger.error(f"Error fetching leaderboard stats: {e}")
            raise
    
    async def get_user_leaderboard_summary(self, user_id: int) -> Dict[str, Any]:
        """Get leaderboard summary for a specific user."""
        try:
            # Get all entries for the user
            user_entries = await self.get_by_user_id(user_id)
            
            if not user_entries:
                return {
                    "user_id": user_id,
                    "total_entries": 0,
                    "best_score": 0.0,
                    "average_score": 0.0,
                    "tasks_participated": 0,
                }
            
            # Calculate statistics
            scores = [entry.score for entry in user_entries]
            task_ids = set(entry.task_id for entry in user_entries)
            
            return {
                "user_id": user_id,
                "total_entries": len(user_entries),
                "best_score": max(scores),
                "average_score": sum(scores) / len(scores),
                "tasks_participated": len(task_ids),
            }
        except Exception as e:
            logger.error(f"Error fetching user leaderboard summary: {e}")
            raise
    
    async def get_agent_leaderboard_summary(self, agent_id: int) -> Dict[str, Any]:
        """Get leaderboard summary for a specific agent."""
        try:
            # Get all entries for the agent
            agent_entries = await self.get_by_agent_id(agent_id)
            
            if not agent_entries:
                return {
                    "agent_id": agent_id,
                    "total_entries": 0,
                    "best_score": 0.0,
                    "average_score": 0.0,
                    "tasks_participated": 0,
                }
            
            # Calculate statistics
            scores = [entry.score for entry in agent_entries]
            task_ids = set(entry.task_id for entry in agent_entries)
            
            return {
                "agent_id": agent_id,
                "total_entries": len(agent_entries),
                "best_score": max(scores),
                "average_score": sum(scores) / len(scores),
                "tasks_participated": len(task_ids),
            }
        except Exception as e:
            logger.error(f"Error fetching agent leaderboard summary: {e}")
            raise
    
    async def update_or_create_entry(
        self, 
        agent_id: int, 
        task_id: int, 
        user_id: int, 
        score: float, 
        submission_id: int
    ) -> LeaderboardEntry:
        """Update existing entry or create new one if score is better."""
        try:
            # Check if entry exists
            existing_entry = await self.db.execute(
                select(LeaderboardEntry).filter(
                    and_(
                        LeaderboardEntry.agent_id == agent_id,
                        LeaderboardEntry.task_id == task_id
                    )
                )
            )
            entry = existing_entry.scalar_one_or_none()
            
            if entry:
                # Update if score is better
                if score > entry.score:
                    entry.score = score
                    entry.submission_id = submission_id
                    entry.updated_at = datetime.utcnow()
                    await self.db.commit()
                    await self.db.refresh(entry)
                    logger.info(f"Updated leaderboard entry for agent {agent_id} in task {task_id}")
                return entry
            else:
                # Create new entry
                entry_data = {
                    "agent_id": agent_id,
                    "task_id": task_id,
                    "user_id": user_id,
                    "score": score,
                    "submission_id": submission_id,
                }
                return await self.create(entry_data)
        except Exception as e:
            logger.error(f"Error updating or creating leaderboard entry: {e}")
            raise
    
    async def get_task_leaderboard_with_details(self, task_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get leaderboard with agent and user details for a task."""
        try:
            # This would typically use joins - simplified for now
            entries = await self.get_top_entries_by_task(task_id, limit)
            
            detailed_entries = []
            for rank, entry in enumerate(entries, 1):
                detailed_entries.append({
                    "rank": rank,
                    "agent_id": entry.agent_id,
                    "user_id": entry.user_id,
                    "score": entry.score,
                    "submission_id": entry.submission_id,
                    "created_at": entry.created_at,
                    "updated_at": entry.updated_at,
                })
            
            return detailed_entries
        except Exception as e:
            logger.error(f"Error fetching detailed leaderboard: {e}")
            raise