"""Agent repository for agent-specific database operations."""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, desc

from .base_repository import BaseRepository
from ..models.agent import Agent
from ..core.logger import get_logger

logger = get_logger(__name__)


class AgentRepository(BaseRepository[Agent]):
    """Repository for agent-specific database operations."""
    
    def __init__(self, db_session: AsyncSession):
        """Initialize the agent repository."""
        super().__init__(db_session, Agent)
    
    async def get_by_name(self, name: str) -> Optional[Agent]:
        """Get an agent by name."""
        return await self.get_by_field("name", name)
    
    async def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Agent]:
        """Get all agents for a specific user."""
        return await self.get_many_by_field("user_id", user_id)
    
    async def get_active_agents(self, skip: int = 0, limit: int = 100) -> List[Agent]:
        """Get all active agents."""
        return await self.get_all(skip=skip, limit=limit, filters={"is_active": True})
    
    async def get_by_provider(self, provider: str, skip: int = 0, limit: int = 100) -> List[Agent]:
        """Get all agents by provider."""
        return await self.get_all(skip=skip, limit=limit, filters={"provider": provider})
    
    async def get_by_user_and_name(self, user_id: int, name: str) -> Optional[Agent]:
        """Get an agent by user ID and name."""
        try:
            result = await self.db.execute(
                select(Agent).filter(
                    and_(
                        Agent.user_id == user_id,
                        Agent.name == name
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching agent by user and name: {e}")
            raise
    
    async def agent_name_exists_for_user(self, user_id: int, name: str) -> bool:
        """Check if agent name already exists for a user."""
        agent = await self.get_by_user_and_name(user_id, name)
        return agent is not None
    
    async def get_top_performing_agents(self, limit: int = 10) -> List[Agent]:
        """Get top performing agents based on performance score."""
        try:
            result = await self.db.execute(
                select(Agent)
                .filter(Agent.is_active == True)
                .order_by(desc(Agent.performance_score))
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching top performing agents: {e}")
            raise
    
    async def update_performance_score(self, agent_id: int, score: float) -> Agent:
        """Update the performance score of an agent."""
        return await self.update(agent_id, {"performance_score": score})
    
    async def activate_agent(self, agent_id: int) -> Agent:
        """Activate an agent."""
        return await self.update(agent_id, {"is_active": True})
    
    async def deactivate_agent(self, agent_id: int) -> Agent:
        """Deactivate an agent."""
        return await self.update(agent_id, {"is_active": False})
    
    async def get_agent_with_submissions(self, agent_id: int) -> Optional[Agent]:
        """Get agent with all its submissions."""
        return await self.get_with_relations(agent_id, ["submissions"])
    
    async def get_agents_by_type(self, agent_type: str, skip: int = 0, limit: int = 100) -> List[Agent]:
        """Get agents by type."""
        return await self.get_all(skip=skip, limit=limit, filters={"type": agent_type})
    
    async def search_agents(self, query: str, skip: int = 0, limit: int = 100) -> List[Agent]:
        """Search agents by name or description."""
        try:
            result = await self.db.execute(
                select(Agent).filter(
                    or_(
                        Agent.name.ilike(f"%{query}%"),
                        Agent.description.ilike(f"%{query}%")
                    )
                ).offset(skip).limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error searching agents: {e}")
            raise
    
    async def get_agent_statistics(self, agent_id: int) -> dict:
        """Get comprehensive statistics for an agent."""
        try:
            agent = await self.get_by_id_or_404(agent_id)
            
            # Basic stats - in a real implementation, this would involve
            # complex queries with joins to submissions, evaluations, etc.
            stats = {
                "agent_id": agent.id,
                "name": agent.name,
                "provider": agent.provider,
                "model": agent.model,
                "created_at": agent.created_at,
                "updated_at": agent.updated_at,
                "is_active": agent.is_active,
                "performance_score": agent.performance_score,
                # Additional stats would be calculated here
                "total_submissions": 0,  # To be calculated
                "successful_submissions": 0,  # To be calculated
                "average_score": 0.0,  # To be calculated
            }
            
            return stats
        except Exception as e:
            logger.error(f"Error fetching agent statistics for agent {agent_id}: {e}")
            raise