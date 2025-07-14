from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..models.agent import Agent
import uuid

class AgentService:
    def __init__(self, db: Session):
        self._db = db

    def create_agent(self, agent_data: dict, user_id: uuid.UUID | str) -> Agent:
        """Create an Agent record while supporting both the extended and
        legacy payload shapes used in the test-suite.

        1.  `config` (legacy) ➜ `configurationJson`
        2.  Unknown / extraneous keys are discarded so we only pass columns
            that actually exist on the SQLAlchemy `Agent` model – otherwise
            SQLAlchemy raises a `TypeError`.
        """

        try:
            # --- 1️⃣  Map legacy aliases --------------------------------------------------
            data = dict(agent_data)  # shallow copy so we can mutate safely

            if "config" in data and data.get("config") is not None:
                # `config` is the simplified alias expected by the e2e tests
                # – map it to the JSON column on the model.
                data["configurationJson"] = data.pop("config")

            # Provide a sensible default if configurationJson is still missing
            data.setdefault("configurationJson", {})

            # --- 2️⃣  Strip unknown fields -----------------------------------------------
            allowed_columns = {c.name for c in Agent.__table__.columns}
            filtered = {k: v for k, v in data.items() if k in allowed_columns}

            # Inject userId (stored as string in DB for convenience)
            filtered["userId"] = str(user_id)

            # --- 3️⃣  Persist -------------------------------------------------------------
            agent = Agent(**filtered)
            self._db.add(agent)
            self._db.commit()
            self._db.refresh(agent)
            return agent
        except Exception as e:
            self._db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def get_user_agents(self, user_id: uuid.UUID | str):
        return self._db.query(Agent).filter(
            Agent.userId == str(user_id),
            Agent.isActive == True
        ).all()

    def get_agent_by_id(self, agent_id: uuid.UUID | str, user_id: uuid.UUID | str) -> Agent:
        agent = self._db.query(Agent).filter(
            Agent.id == str(agent_id),
            Agent.userId == str(user_id),
            Agent.isActive == True
        ).first()
        if not agent:
            from ..core.exceptions import NotFoundException
            raise NotFoundException("Agent not found")
        return agent