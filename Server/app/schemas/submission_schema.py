from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from ..models.enums import SubmissionStatus, EvaluationStatus

class SubmissionCreate(BaseModel):
    # Accept both camelCase and snake_case for backward compatibility
    agentId: Optional[str] = None
    taskId: Optional[str] = None
    agent_id: Optional[str | int] = None  # Support numeric IDs used in tests
    task_id: Optional[str | int] = None
    run_config: Optional[Dict[str, Any]] = {}

    @property
    def agentId_resolved(self) -> str:
        value = self.agentId if self.agentId is not None else self.agent_id
        return str(value) if value is not None else ""  # type: ignore

    @property
    def taskId_resolved(self) -> str:
        value = self.taskId if self.taskId is not None else self.task_id
        return str(value) if value is not None else ""  # type: ignore

class EvaluationResultResponse(BaseModel):
    score: float
    timeTaken: float
    accuracy: float
    completedAt: datetime
    status: EvaluationStatus
    resultDetails: Dict[str, Any]
    playgroundRawScore: Optional[float] = None
    playgroundTaskCompleted: Optional[bool] = None
    playgroundEfficiencyScore: Optional[float] = None
    playgroundTimeScore: Optional[float] = None

class PlaygroundDetailsResponse(BaseModel):
    success: bool
    execution_time: Optional[float] = None
    steps_taken: Optional[int] = None
    screenshots_count: int = 0
    trace_file: Optional[str] = None
    error_details: Optional[str] = None

class SubmissionResponse(BaseModel):
    id: UUID
    agentId: UUID
    taskId: UUID
    userId: UUID
    status: SubmissionStatus
    submittedAt: datetime
    completedAt: Optional[datetime] = None
    result: Optional[EvaluationResultResponse] = None
    playgroundDetails: Optional[PlaygroundDetailsResponse] = None
    # Legacy flat fields to support older test-suite expectations
    playground_execution_id: Optional[str] = None
    steps_taken: Optional[int] = None
    execution_time_seconds: Optional[float] = None
    success_rate: Optional[float] = None
    result_data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class LeaderboardResponse(BaseModel):
    rank: int
    agentName: str
    agentId: UUID
    taskId: UUID
    submissionId: UUID
    score: float
    timeTaken: float
    accuracy: float

    class Config:
        from_attributes = True

class SubmissionListResponse(BaseModel):
    items: List[SubmissionResponse]
    total: int

    class Config:
        from_attributes = True
