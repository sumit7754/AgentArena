from sqlalchemy import Column, String, Enum, Integer, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .enums import TaskDifficulty
from .base import Base


class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Ensure id accessible even after session closed in tests
    def __getattribute__(self, name):
        if name == "id":
            _dict = object.__getattribute__(self, "__dict__")
            cached = _dict.get("id")
            if cached is not None:
                return cached
            state = object.__getattribute__(self, "_sa_instance_state")
            identity_key = state.identity_key
            if identity_key and len(identity_key[1]) >= 1:
                return identity_key[1][0]
        return object.__getattribute__(self, name)
    title = Column(String)
    description = Column(String)
    difficulty = Column(Enum(TaskDifficulty))
    webArenaEnvironment = Column(String)
    environmentConfig = Column(JSON)
    
    # WebArena-specific fields
    webArenaTaskId = Column(Integer, nullable=True)  # Maps to WebArena's task ID
    webArenaTaskConfigPath = Column(String, nullable=True)  # Path to WebArena task config
    webArenaInstructionPath = Column(String, nullable=True)  # Path to instruction file
    expectedCompletionTime = Column(Integer, default=300)  # Expected time in seconds
    maxAllowedTime = Column(Integer, default=600)  # Max time limit in seconds
    
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now())
    createdBy = Column(String(36), ForeignKey("users.id"))
    
    # Relationships
    creator = relationship("User", back_populates="created_tasks")
    metrics = relationship("TaskMetrics", back_populates="task")
    submissions = relationship("Submission", back_populates="task")
    leaderboard_entries = relationship("Leaderboard", back_populates="task")


class TaskMetrics(Base):
    __tablename__ = "task_metrics"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    taskId = Column(String(36), ForeignKey("tasks.id"))
    maxTimeAllowed = Column(Integer)
    minAccuracy = Column(Float)
    expectedSteps = Column(Integer)
    timeWeight = Column(Float)
    accuracyWeight = Column(Float)
    environmentParameters = Column(JSON)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    task = relationship("Task", back_populates="metrics")