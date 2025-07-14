from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from ..models.enums import TaskDifficulty


class PlaygroundRunStatus(str, Enum):
    """Status enum for playground execution."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"


class PlaygroundRunInput(BaseModel):
    """Input schema for playground execution - the interface between SubmissionService and IPlaygroundExecutionService."""
    
    # Core identifiers
    submission_id: str
    user_id: str
    agent_id: str
    task_id: str
    
    # Agent details
    agent_name: str
    agent_description: Optional[str] = None
    agent_configuration: Dict[str, Any]
    agent_type: str = "gpt-4"
    llm_api_key: Optional[str] = None  # Encrypted, to be decrypted by playground service
    
    # Task details  
    task_title: str
    task_description: str
    task_difficulty: TaskDifficulty
    web_arena_environment: str
    environment_config: Dict[str, Any]
    web_arena_task_id: Optional[int] = None
    web_arena_task_config_path: Optional[str] = None
    web_arena_instruction_path: Optional[str] = None
    expected_completion_time: int = 300
    max_allowed_time: int = 600
    
    # Runtime configuration
    max_steps: int = 100
    timeout_seconds: int = 600


class PlaygroundRunOutput(BaseModel):
    """Output schema from playground execution - returned to SubmissionService for processing."""
    
    # Execution status
    status: PlaygroundRunStatus
    execution_id: str
    
    # Performance metrics
    steps_taken: int
    total_time_seconds: float
    success_rate: float
    
    # Error handling
    error_message: Optional[str] = None
    
    # Detailed execution information
    execution_log: List[str] = []
    result_data: Dict[str, Any] = {}


class PlaygroundStatus(BaseModel):
    """Status information for ongoing playground executions."""
    
    # Required fields
    submission_id: str
    execution_id: str  # Required field that was missing
    status: str  # QUEUED, RUNNING, COMPLETED, FAILED
    
    # Progress tracking
    progress: Optional[float] = 0.0  # Progress value (0.0 to 1.0)
    progress_percentage: float = 0.0
    current_step: int = 0
    
    # Timing information
    start_time: float  # Required field that was missing
    end_time: Optional[float] = None
    estimated_remaining_seconds: Optional[int] = None
    
    # Status details
    last_action: Optional[str] = None
    error_message: Optional[str] = None
    logs: List[str] = []  # Optional field for consistency