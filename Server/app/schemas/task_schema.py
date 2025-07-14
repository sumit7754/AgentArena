from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from .enums import TaskDifficulty

class TaskCreate(BaseModel):
    title: str
    description: str
    difficulty: TaskDifficulty
    # Accept both camelCase and snake_case / legacy fields
    webArenaEnvironment: Optional[str] = None
    environmentConfig: Optional[Dict[str, Any]] = {}
    # Legacy aliases expected by e2e tests
    category: Optional[str] = None  # maps to webArenaEnvironment
    task_config: Optional[Dict[str, Any]] = None  # maps to environmentConfig

    @classmethod
    def _preprocess(cls, values):
        # Map legacy fields to new ones before validation completes
        if "webArenaEnvironment" not in values or values.get("webArenaEnvironment") is None:
            if "category" in values and values["category"] is not None:
                values["webArenaEnvironment"] = values["category"]
        if ("environmentConfig" not in values or values.get("environmentConfig") in (None, {})) and (
            "task_config" in values and values["task_config"] is not None
        ):
            values["environmentConfig"] = values["task_config"]
        return values

    from pydantic import root_validator
    _legacy_aliases = root_validator(pre=True, allow_reuse=True)(_preprocess)

    _difficulty_alias = root_validator(pre=True, allow_reuse=True)(
        lambda cls, v: {**v, "difficulty": v.get("difficulty").upper() if isinstance(v.get("difficulty"), str) else v.get("difficulty")}
    )

    # WebArena-specific fields
    webArenaTaskId: Optional[int] = None
    webArenaTaskConfigPath: Optional[str] = None
    webArenaInstructionPath: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[TaskDifficulty] = None
    webArenaEnvironment: Optional[str] = None
    environmentConfig: Optional[Dict[str, Any]] = None
    # WebArena-specific update fields
    webArenaTaskId: Optional[int] = None
    webArenaTaskConfigPath: Optional[str] = None
    webArenaInstructionPath: Optional[str] = None

class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    difficulty: TaskDifficulty
    webArenaEnvironment: str
    environmentConfig: Dict[str, Any]
    createdAt: datetime
    updatedAt: Optional[datetime] = None
    # WebArena-specific response fields
    webArenaTaskId: Optional[int] = None
    webArenaTaskConfigPath: Optional[str] = None
    webArenaInstructionPath: Optional[str] = None

    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    items: List[TaskResponse]
    total: int
    page: int
    size: int

    class Config:
        extra = "allow"