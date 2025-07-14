from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, Integer, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .base import Base


class Leaderboard(Base):
    __tablename__ = "leaderboard"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    taskId = Column(String(36), ForeignKey("tasks.id"))
    agentId = Column(String(36), ForeignKey("agents.id"))
    submissionId = Column(String(36), ForeignKey("submissions.id"))
    score = Column(Float)
    rank = Column(Integer)
    timeTaken = Column(Float)
    accuracy = Column(Float)
    
    # WebArena-specific leaderboard fields
    webArenaSteps = Column(Integer, nullable=True)  # Steps taken
    webArenaSuccess = Column(Boolean, nullable=True)  # Success status
    webArenaEfficiency = Column(Float, nullable=True)  # Efficiency metric
    
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    task = relationship("Task", back_populates="leaderboard_entries")
    agent = relationship("Agent", back_populates="leaderboard_entries")
    submission = relationship("Submission", back_populates="leaderboard_entry")