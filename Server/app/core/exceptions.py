"""Custom exception classes for the AgentArena application."""

from typing import Optional, Any, Dict
from fastapi import HTTPException, status


class AgentArenaException(HTTPException):
    """Base exception class for AgentArena with HTTP status code support."""
    
    def __init__(
        self, 
        message: str, 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        
        # Format detail for FastAPI
        detail = {
            "message": message,
            "error_code": error_code,
            "details": self.details
        }
        
        super().__init__(status_code=status_code, detail=detail)


class NotFoundException(AgentArenaException):
    """Raised when a requested resource is not found."""
    
    def __init__(
        self, 
        message: str = "Resource not found", 
        error_code: str = "NOT_FOUND",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None
    ):
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id
            
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=error_code,
            details=details
        )


class UnauthorizedException(AgentArenaException):
    """Raised when user is not authorized to perform an action."""
    
    def __init__(
        self, 
        message: str = "Unauthorized access", 
        error_code: str = "UNAUTHORIZED",
        required_permission: Optional[str] = None
    ):
        details = {}
        if required_permission:
            details["required_permission"] = required_permission
            
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=error_code,
            details=details
        )


class ForbiddenException(AgentArenaException):
    """Raised when user lacks permission to perform an action."""
    
    def __init__(
        self, 
        message: str = "Forbidden - insufficient permissions", 
        error_code: str = "FORBIDDEN",
        required_role: Optional[str] = None
    ):
        details = {}
        if required_role:
            details["required_role"] = required_role
            
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=error_code,
            details=details
        )


class ValidationException(AgentArenaException):
    """Raised when input validation fails."""
    
    def __init__(
        self, 
        message: str = "Invalid input", 
        error_code: str = "VALIDATION_ERROR",
        field_errors: Optional[Dict[str, str]] = None
    ):
        details = {}
        if field_errors:
            details["field_errors"] = field_errors
            
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=error_code,
            details=details
        )


class PlaygroundExecutionException(AgentArenaException):
    """Raised when playground execution fails."""
    
    def __init__(
        self, 
        message: str = "Playground execution failed", 
        error_code: str = "PLAYGROUND_EXECUTION_ERROR",
        execution_id: Optional[str] = None,
        step_number: Optional[int] = None
    ):
        details = {}
        if execution_id:
            details["execution_id"] = execution_id
        if step_number:
            details["step_number"] = step_number
            
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=error_code,
            details=details
        )


class DatabaseException(AgentArenaException):
    """Raised when database operations fail."""
    
    def __init__(
        self, 
        message: str = "Database operation failed", 
        error_code: str = "DATABASE_ERROR",
        operation: Optional[str] = None
    ):
        details = {}
        if operation:
            details["operation"] = operation
            
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=error_code,
            details=details
        )


class ConfigurationException(AgentArenaException):
    """Raised when there are configuration issues."""
    
    def __init__(
        self, 
        message: str = "Configuration error", 
        error_code: str = "CONFIGURATION_ERROR",
        config_key: Optional[str] = None
    ):
        details = {}
        if config_key:
            details["config_key"] = config_key
            
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=error_code,
            details=details
        )


class AgentException(AgentArenaException):
    """Raised when agent-related operations fail."""
    
    def __init__(
        self, 
        message: str = "Agent operation failed", 
        error_code: str = "AGENT_ERROR",
        agent_id: Optional[str] = None
    ):
        details = {}
        if agent_id:
            details["agent_id"] = agent_id
            
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=error_code,
            details=details
        )


class TaskException(AgentArenaException):
    """Raised when task-related operations fail."""
    
    def __init__(
        self, 
        message: str = "Task operation failed", 
        error_code: str = "TASK_ERROR",
        task_id: Optional[str] = None
    ):
        details = {}
        if task_id:
            details["task_id"] = task_id
            
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=error_code,
            details=details
        )


class SubmissionException(AgentArenaException):
    """Raised when submission-related operations fail."""
    
    def __init__(
        self, 
        message: str = "Submission operation failed", 
        error_code: str = "SUBMISSION_ERROR",
        submission_id: Optional[str] = None
    ):
        details = {}
        if submission_id:
            details["submission_id"] = submission_id
            
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=error_code,
            details=details
        )


class ExternalServiceException(AgentArenaException):
    """Raised when external service calls fail."""
    
    def __init__(
        self, 
        message: str = "External service error", 
        error_code: str = "EXTERNAL_SERVICE_ERROR",
        service_name: Optional[str] = None,
        service_error: Optional[str] = None
    ):
        details = {}
        if service_name:
            details["service_name"] = service_name
        if service_error:
            details["service_error"] = service_error
            
        super().__init__(
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code=error_code,
            details=details
        )


class RateLimitException(AgentArenaException):
    """Raised when rate limits are exceeded."""
    
    def __init__(
        self, 
        message: str = "Rate limit exceeded", 
        error_code: str = "RATE_LIMIT_EXCEEDED",
        retry_after: Optional[int] = None
    ):
        details = {}
        if retry_after:
            details["retry_after"] = retry_after
            
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code=error_code,
            details=details
        )