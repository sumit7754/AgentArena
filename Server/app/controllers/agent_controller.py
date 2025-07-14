from fastapi import HTTPException
from ..services.agent_service import AgentService
from ..schemas.agent_schema import AgentCreate, AgentResponse
from sqlalchemy.orm import Session
import uuid

class AgentController:
    def __init__(self, db: Session):
        self.agent_service = AgentService(db)

    async def create_agent(self, agent_data: AgentCreate, user_id: uuid.UUID) -> AgentResponse:
        agent = self.agent_service.create_agent(agent_data.dict(), user_id)
        return AgentResponse.from_orm(agent)

    async def get_user_agents(self, user_id: uuid.UUID):
        agents = self.agent_service.get_user_agents(user_id)
        return [AgentResponse.from_orm(agent) for agent in agents]

    async def get_agent(self, agent_id: str, user_id: uuid.UUID) -> AgentResponse:
        try:
            agent_uuid = uuid.UUID(agent_id)
            agent = self.agent_service.get_agent_by_id(agent_uuid, user_id)
            return AgentResponse.from_orm(agent)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid agent ID")