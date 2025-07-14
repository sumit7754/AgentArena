# Server/app/schemas/playground.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum

class PlaygroundRunStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class PlaygroundStatus(BaseModel):
    submission_id: str = Field(..., description="Unique ID for the associated submission.")
    execution_id: str = Field(..., description="Unique ID for this specific playground execution.")
    status: PlaygroundRunStatus = Field(..., description="Current status of the playground run.")
    progress: float = Field(0.0, ge=0.0, le=1.0, description="Progress of the run (0.0 to 1.0).")
    progress_percentage: int = Field(0, ge=0, le=100, description="Progress in percentage (0 to 100).")
    start_time: float = Field(..., description="Timestamp when the execution started (Unix timestamp).")
    end_time: Optional[float] = Field(None, description="Timestamp when the execution ended (Unix timestamp).")
    error_message: Optional[str] = Field(None, description="Error message if the run failed.")
    logs: List[str] = Field([], description="Recent execution logs.")

class PlaygroundRunInput(BaseModel):
    submission_id: str = Field(..., description="Unique ID for the associated submission.")
    agent_name: str = Field(..., description="Name of the agent being evaluated.")
    agent_configuration: Dict[str, Any] = Field(..., description="Configuration specific to the agent (e.g., LLM parameters).")
    llm_api_key: Optional[str] = Field(None, description="Temporary API key for the LLM, if required and not globally configured.")
    agent_details: Dict[str, Any] = Field(..., description="Details about the agent, including its code content.")
    task_title: str = Field(..., description="Title of the task to be performed.")
    task_description: str = Field(..., description="Detailed description of the task.")
    task_difficulty: str = Field(..., description="Difficulty level of the task.")
    web_arena_environment: str = Field(..., description="Type of WebArena environment (e.g., 'omnizon', 'web_Browse').")
    environment_config: Dict[str, Any] = Field(..., description="Configuration specific to the environment (e.g., initial URL).")
    task_configuration: Dict[str, Any] = Field(..., description="Full task configuration including success criteria.")

class PlaygroundRunOutput(BaseModel):
    status: PlaygroundRunStatus = Field(..., description="Final status of the playground run.")
    execution_id: str = Field(..., description="Unique ID for this specific playground execution.")
    steps_taken: int = Field(..., description="Number of steps the agent took to complete the task.")
    total_time_seconds: float = Field(..., description="Total time taken for the execution in seconds.")
    success_rate: float = Field(..., ge=0.0, le=1.0, description="Success rate of the execution (0.0 to 1.0).")
    error_message: Optional[str] = Field(None, description="Error message if the run failed.")
    execution_log: List[str] = Field(..., description="Detailed log of agent's actions and observations.")
    result_data: Dict[str, Any] = Field(..., description="Additional data related to the execution result (e.g., final screenshot, browser state).")