from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...db.database import get_db
from ...controllers.agent_controller import AgentController
from ...schemas.agent_schema import AgentCreate, AgentResponse, AgentCreateLegacy
from ...core.security import get_current_user
from ...models.user import User
from ...models.enums import UserRole
from typing import List
from uuid import UUID
import uuid

router = APIRouter(prefix="/agents", tags=["Agents"])

@router.post("/extended", response_model=AgentResponse)
async def create_agent(
    agent: AgentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    controller = AgentController(db)
    return await controller.create_agent(agent, current_user.id)

@router.get("/extended", response_model=List[AgentResponse])
async def get_my_agents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    controller = AgentController(db)
    return await controller.get_user_agents(current_user.id)

@router.get("/extended/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    try:
        agent_uuid = UUID(agent_id)
    except ValueError:
        from ...core.exceptions import NotFoundException
        # For backward-compat, treat non-UUID IDs as not found (404)
        raise NotFoundException("Agent not found")

    controller = AgentController(db)
    return await controller.get_agent(agent_uuid, current_user.id)

# -----------------------------------------------------------------------------
# Legacy simplified agents endpoints expected by e2e tests
# -----------------------------------------------------------------------------

@router.post("", status_code=201)
async def create_agent_legacy(
    agent: AgentCreateLegacy,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create agent using simplified payload."""
    from ...services.agent_service import AgentService  # local import to avoid cycle
    service = AgentService(db)
    agent_record = service.create_agent(agent.dict(exclude_unset=True), current_user.id)
    return {
        "id": agent_record.id,
        "name": agent.name,
        "description": agent.description,
        "config": agent.configurationJson or {},
        "created_at": str(agent_record.createdAt),
    }

@router.get("", status_code=200)
async def list_agents_legacy(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from ...services.agent_service import AgentService
    service = AgentService(db)
    agents = service.get_user_agents(current_user.id)
    items = [
        {
            "id": a.id,
            "name": getattr(a, "name", "Agent"),
            "description": getattr(a, "description", ""),
            "created_at": str(a.createdAt) if hasattr(a, "createdAt") else None,
        }
        for a in agents
    ]
    return {"items": items, "total": len(items)}

@router.get("/{agent_id}", status_code=200)
async def get_agent_legacy(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from ...services.agent_service import AgentService
    try:
        uuid.UUID(agent_id)
    except ValueError:
        # For backward-compat, treat non-UUID IDs as not found (404) instead of bad request.
        from ...core.exceptions import NotFoundException
        raise NotFoundException("Agent not found")
    service = AgentService(db)
    agent = service.get_agent_by_id(agent_id, current_user.id)
    return {
        "id": agent.id,
        "name": getattr(agent, "name", "Agent"),
        "description": getattr(agent, "description", ""),
    }