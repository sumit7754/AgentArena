from sqlalchemy import Column, String, ForeignKey, JSON, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .base import Base


class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Ensure `obj.id` is safe to access after the session is closed (tests rely on it)
    def __getattribute__(self, name):
        if name == "id":
            # Return cached value without triggering a DB fetch
            _dict = object.__getattribute__(self, "__dict__")
            cached = _dict.get("id")
            if cached is not None:
                return cached
            # Fallback: fetch from SQLAlchemy identity key without touching DB
            state = object.__getattribute__(self, "_sa_instance_state")
            identity_key = state.identity_key
            if identity_key and len(identity_key[1]) >= 1:
                return identity_key[1][0]
        return object.__getattribute__(self, name)
    userId = Column(String(36), ForeignKey("users.id"))
    name = Column(String)
    description = Column(String, nullable=True)
    configurationJson = Column(JSON)
    
    # WebArena-specific fields
    llmApiKey = Column(String, nullable=True)  # Encrypted LLM API key
    agentType = Column(String, default="gpt-4")  # Agent type for WebArena
    
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now())
    isActive = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="agents")
    submissions = relationship("Submission", back_populates="agent")
    leaderboard_entries = relationship("Leaderboard", back_populates="agent")