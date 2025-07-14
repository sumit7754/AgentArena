from enum import Enum

class TaskDifficulty(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"

class SubmissionStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    QUEUED = "QUEUED"

class EvaluationStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER" 