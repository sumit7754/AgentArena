from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid

class AgentCapabilities(str, Enum):
    WEB_NAVIGATION = "web_navigation"
    TEXT_PROCESSING = "text_processing"
    DATA_EXTRACTION = "data_extraction"
    FORM_FILLING = "form_filling"
    VISUAL_PROCESSING = "visual_processing"
    REASONING = "reasoning"
    PLANNING = "planning"
    MULTI_STEP_WORKFLOWS = "multi_step_workflows"

class AgentProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    CUSTOM = "custom"
    LOCAL = "local"

class BrowserEngine(str, Enum):
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"
    CUSTOM = "custom"

class AgentArchitecture(str, Enum):
    SINGLE_AGENT = "single_agent"
    MULTI_AGENT = "multi_agent"
    HIERARCHICAL = "hierarchical"
    COLLABORATIVE = "collaborative"

class AgentFramework(str, Enum):
    LANGCHAIN = "langchain"
    AUTOGEN = "autogen"
    CREWAI = "crewai"
    CUSTOM = "custom"
    NATIVE = "native"

class AgentSystemInfo(BaseModel):
    """Detailed system and hardware information for the agent"""
    operating_system: Optional[str] = None
    browser_engine: BrowserEngine = BrowserEngine.CHROMIUM
    browser_version: Optional[str] = None
    screen_resolution: Optional[str] = None
    viewport_size: Optional[str] = "1280x720"
    user_agent: Optional[str] = None
    network_conditions: Optional[Dict[str, Any]] = None
    hardware_acceleration: bool = True

class AgentConfiguration(BaseModel):
    """Comprehensive agent configuration similar to realevals.xyz"""
    # Model Configuration
    model_name: str = Field(..., description="Primary model (e.g., gpt-4, claude-3-sonnet)")
    model_version: Optional[str] = None
    backup_model: Optional[str] = None
    temperature: float = Field(0.1, ge=0.0, le=2.0)
    max_tokens: int = Field(2000, gt=0, le=8000)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    frequency_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0)
    presence_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0)
    
    # Agent Behavior
    system_prompt: str = Field(..., min_length=10, max_length=2000)
    planning_strategy: str = "step_by_step"
    error_handling: str = "retry_with_backoff"
    max_retries: int = Field(3, ge=0, le=10)
    timeout_seconds: int = Field(300, gt=0, le=1800)
    
    # Execution Parameters
    max_steps: int = Field(50, gt=0, le=200)
    think_before_action: bool = True
    screenshot_frequency: str = "on_action"  # on_action, every_step, never
    action_delay: float = Field(1.0, ge=0.0, le=10.0)
    page_load_timeout: int = Field(30, gt=0, le=120)
    
    # Observation Settings
    include_html: bool = False
    include_accessibility_tree: bool = True
    include_screenshots: bool = True
    max_screenshot_size: str = "1920x1080"
    element_highlighting: bool = True
    
    # Memory and Context
    memory_type: str = "conversation"  # conversation, semantic, episodic
    context_window: int = Field(4000, gt=0, le=32000)
    preserve_session: bool = True
    clear_memory_frequency: str = "per_task"  # per_task, per_session, never
    
    # Safety and Constraints
    allowed_domains: Optional[List[str]] = None
    blocked_domains: Optional[List[str]] = None
    safe_mode: bool = True
    content_filtering: bool = True
    privacy_mode: bool = False

class AgentMetadata(BaseModel):
    """Rich metadata about the agent similar to realevals.xyz"""
    # Agent Identity
    display_name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    version: str = "1.0.0"
    author: Optional[str] = None
    organization: Optional[str] = None
    contact_email: Optional[str] = None
    
    # Technical Details
    agent_type: str = Field(..., description="Primary model family")
    provider: AgentProvider = AgentProvider.OPENAI
    architecture: AgentArchitecture = AgentArchitecture.SINGLE_AGENT
    framework: AgentFramework = AgentFramework.NATIVE
    
    # Capabilities
    capabilities: List[AgentCapabilities] = []
    supported_environments: List[str] = []
    specialized_domains: List[str] = []
    
    # Performance Characteristics
    expected_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0)
    average_response_time: Optional[float] = None
    resource_requirements: Optional[Dict[str, Any]] = None
    
    # Documentation
    documentation_url: Optional[str] = None
    source_code_url: Optional[str] = None
    demo_video_url: Optional[str] = None
    research_paper_url: Optional[str] = None

class AgentCreate(BaseModel):
    """Enhanced agent creation request with comprehensive information"""
    # Basic Information
    metadata: AgentMetadata
    configuration: AgentConfiguration
    system_info: Optional[AgentSystemInfo] = None
    
    # API Configuration
    llm_api_key: Optional[str] = Field(None, description="Encrypted API key for LLM provider")
    api_base_url: Optional[str] = None
    custom_headers: Optional[Dict[str, str]] = None
    
    # Testing Preferences
    preferred_test_environments: List[str] = []
    avoid_environments: List[str] = []
    testing_notes: Optional[str] = None

class AgentUpdate(BaseModel):
    """Update agent information"""
    metadata: Optional[AgentMetadata] = None
    configuration: Optional[AgentConfiguration] = None
    system_info: Optional[AgentSystemInfo] = None
    llm_api_key: Optional[str] = None
    is_active: Optional[bool] = None

class AgentResponse(BaseModel):
    """Enhanced agent response with all information"""
    id: str
    userId: str
    
    # Core Information
    metadata: AgentMetadata
    configuration: AgentConfiguration
    system_info: AgentSystemInfo
    
    # Status
    is_active: bool
    has_api_key: bool
    is_verified: bool = False
    last_tested: Optional[datetime] = None
    
    # Performance Metrics
    total_submissions: int = 0
    successful_submissions: int = 0
    average_score: float = 0.0
    best_score: float = 0.0
    average_completion_time: float = 0.0
    
    # System Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Leaderboard Position
    global_rank: Optional[int] = None
    category_ranks: Optional[Dict[str, int]] = None

    class Config:
        from_attributes = True

class AgentSubmissionInfo(BaseModel):
    """Information collected when submitting agent to task"""
    agent_id: str
    task_id: str
    
    # Runtime Configuration Override
    runtime_config: Optional[Dict[str, Any]] = None
    custom_system_prompt: Optional[str] = None
    max_steps_override: Optional[int] = None
    timeout_override: Optional[int] = None
    
    # Submission Metadata
    submission_notes: Optional[str] = None
    expected_outcome: Optional[str] = None
    testing_focus: Optional[str] = None

class AgentPerformanceStats(BaseModel):
    """Detailed performance statistics for an agent"""
    agent_id: str
    agent_name: str
    
    # Overall Performance
    total_tasks_attempted: int
    total_tasks_completed: int
    success_rate: float
    average_score: float
    median_score: float
    best_score: float
    worst_score: float
    
    # Time Performance
    average_completion_time: float
    fastest_completion_time: float
    slowest_completion_time: float
    
    # Task Breakdown
    performance_by_difficulty: Dict[str, Dict[str, float]]
    performance_by_environment: Dict[str, Dict[str, float]]
    
    # Recent Performance
    last_7_days: Dict[str, float]
    last_30_days: Dict[str, float]
    
    # Rankings
    global_rank: Optional[int] = None
    category_ranks: Dict[str, int] = {}

class AgentLeaderboardEntry(BaseModel):
    """Agent entry for leaderboard display"""
    rank: int
    agent_id: str
    agent_name: str
    user_name: str
    score: float
    submissions: int
    success_rate: float
    average_time: float
    last_activity: datetime
    badge: Optional[str] = None  # gold, silver, bronze, rising_star, etc.

# Legacy compatibility
class AgentCreateLegacy(BaseModel):
    """Legacy agent creation for backward compatibility"""
    from pydantic import Field
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    agentType: str = "gpt-4"
    configurationJson: Optional[Dict[str, Any]] = {}
    config: Optional[Dict[str, Any]] = None  # legacy alias
    llmApiKey: Optional[str] = None

    # map alias before validation
    @classmethod
    def _alias_mapper(cls, values):
        if "configurationJson" not in values or values.get("configurationJson") in (None, {}):
            if "config" in values and values["config"] is not None:
                values["configurationJson"] = values["config"]
        return values

    from pydantic import root_validator
    _legacy_aliases = root_validator(pre=True, allow_reuse=True)(_alias_mapper)