from sqlalchemy import Column, String, Enum, ForeignKey, DateTime, Boolean, Integer, Float, Text, JSON
from sqlalchemy.orm import relationship, synonym
from sqlalchemy.sql import func
import uuid
from .enums import SubmissionStatus
from .base import Base


class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    userId = Column(String(36), ForeignKey("users.id"))
    agentId = Column(String(36), ForeignKey("agents.id"))
    taskId = Column(String(36), ForeignKey("tasks.id"))
    status = Column(String)  # Using string instead of enum for simplicity
    submittedAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now())
    createdAt = Column(DateTime(timezone=True), server_default=func.now())  # Added for consistency
    
    # Execution tracking fields
    runConfig = Column(JSON, nullable=True)  # Configuration used for the run
    playground_execution_id = Column(String, nullable=True)  # ID from playground service
    steps_taken = Column(Integer, nullable=True)  # Number of steps taken
    execution_time_seconds = Column(Float, nullable=True)  # Actual execution time
    success_rate = Column(Float, nullable=True)  # Success rate from playground
    execution_log = Column(JSON, nullable=True)  # Execution log entries
    result_data = Column(JSON, nullable=True)  # Result data from playground
    error_message = Column(Text, nullable=True)  # Error message if failed
    
    # WebArena-specific fields (kept for compatibility)
    webArenaLogPath = Column(String, nullable=True)  # Path to WebArena execution logs
    webArenaTraceFile = Column(String, nullable=True)  # Path to HTML trace file
    webArenaSuccess = Column(Boolean, nullable=True)  # Success flag from WebArena
    webArenaStepsTaken = Column(Integer, nullable=True)  # Number of steps taken
    webArenaExecutionTime = Column(Float, nullable=True)  # Actual execution time
    webArenaErrorDetails = Column(Text, nullable=True)  # Error details if failed
    webArenaScreenshots = Column(JSON, nullable=True)  # Paths to screenshots
    
    # ------------------------------------------------------------------
    # Compatibility attribute synonyms (snake_case used in test-suite)
    # ------------------------------------------------------------------

    # SQLAlchemy synonym provides alternate attribute name that maps to same column
    agent_id = synonym("agentId")
    task_id = synonym("taskId")
    user_id = synonym("userId")
    
    # Alias for snake_case naming
    run_config = synonym("runConfig")
    
    # Relationships
    user = relationship("User", back_populates="submissions")
    agent = relationship("Agent", back_populates="submissions")
    task = relationship("Task", back_populates="submissions")
    evaluation = relationship("EvaluationResult", back_populates="submission", uselist=False)
    leaderboard_entry = relationship("Leaderboard", back_populates="submission", uselist=False)