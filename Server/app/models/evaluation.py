from sqlalchemy import Column, String, Enum, ForeignKey, DateTime, Boolean, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .enums import EvaluationStatus
from .base import Base


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    submissionId = Column(String(36), ForeignKey("submissions.id"))
    score = Column(Float)
    timeTaken = Column(Float)
    accuracy = Column(Float)
    completedAt = Column(DateTime(timezone=True))
    resultDetails = Column(JSON)
    status = Column(Enum(EvaluationStatus))
    
    # WebArena-specific evaluation fields
    webArenaRawScore = Column(Float, nullable=True)  # Raw WebArena score
    webArenaTaskCompleted = Column(Boolean, nullable=True)  # Task completion status
    webArenaEfficiencyScore = Column(Float, nullable=True)  # Steps efficiency
    webArenaTimeScore = Column(Float, nullable=True)  # Time efficiency
    webArenaDetailsJson = Column(JSON, nullable=True)  # Detailed WebArena results
    
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    submission = relationship("Submission", back_populates="evaluation")