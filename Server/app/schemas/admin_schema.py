from pydantic import BaseModel, EmailStr
from typing import Dict, List, Any, Optional
from datetime import datetime
from ..models.enums import UserRole, TaskDifficulty

class AdminDashboardStats(BaseModel):
    platform_overview: Dict[str, int]
    task_distribution: Dict[str, int]
    submission_metrics: Dict[str, Any]
    activity_metrics: Dict[str, Any]
    environment_usage: Dict[str, int]
    system_health: Dict[str, str]

class UserManagementRequest(BaseModel):
    user_id: str
    reason: Optional[str] = None

class TaskAnalytics(BaseModel):
    task_performance: List[Dict[str, Any]]
    difficulty_analysis: Dict[str, Dict[str, Any]]
    environment_performance: Dict[str, Dict[str, Any]]

class UserAnalytics(BaseModel):
    registration_trend: List[Dict[str, Any]]
    top_performers: List[Dict[str, Any]]
    agent_distribution: Dict[str, int]
    user_engagement: Dict[str, Any]

class SystemMonitoring(BaseModel):
    active_evaluations: int
    queue_length: int
    processing_count: int
    recent_completions: int
    system_load: Dict[str, int]
    active_submissions: List[Dict[str, Any]]

class LeaderboardInsights(BaseModel):
    global_leaderboard: List[Dict[str, Any]]
    task_leaderboards: Dict[str, Dict[str, Any]]
    performance_trends: Dict[str, Any]

class AdminUserResponse(BaseModel):
    id: str
    email: EmailStr
    firstName: str
    lastName: Optional[str]
    role: UserRole
    isActive: bool
    isEmailVerified: bool
    createdAt: datetime
    lastLoginAt: Optional[datetime]
    loginCount: int
    
    class Config:
        from_attributes = True

class AdminTaskResponse(BaseModel):
    id: str
    title: str
    description: str
    difficulty: TaskDifficulty
    webArenaEnvironment: str
    expectedCompletionTime: int
    maxAllowedTime: int
    createdAt: datetime
    submission_count: Optional[int] = 0
    average_score: Optional[float] = 0.0
    
    class Config:
        from_attributes = True

class AdminAgentResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    agentType: str
    user_email: str
    isActive: bool
    createdAt: datetime
    submission_count: Optional[int] = 0
    average_score: Optional[float] = 0.0
    
    class Config:
        from_attributes = True

class PlatformMetrics(BaseModel):
    total_users: int
    active_users: int
    total_agents: int
    total_tasks: int
    total_submissions: int
    success_rate: float
    average_score: float
    uptime: str

class EnvironmentStats(BaseModel):
    environment_name: str
    total_tasks: int
    total_submissions: int
    average_score: float
    success_rate: float
    popular_agent_types: List[str]

class AdminCreateTaskRequest(BaseModel):
    title: str
    description: str
    difficulty: TaskDifficulty
    webArenaEnvironment: str
    webArenaTaskId: Optional[int]
    expectedCompletionTime: int
    maxAllowedTime: int
    environmentConfig: Dict[str, Any]

class BulkUserAction(BaseModel):
    user_ids: List[str]
    action: str  # activate, deactivate, promote, demote
    reason: Optional[str] = None

class SystemHealthCheck(BaseModel):
    database_status: str
    api_status: str
    evaluation_service: str
    memory_usage: Optional[float]
    cpu_usage: Optional[float]
    disk_usage: Optional[float]
    last_check: datetime