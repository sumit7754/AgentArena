from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional, Any, Dict
from pathlib import Path
import os
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # Application settings
    APP_NAME: str = "AgentArena"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    ENVIRONMENT: str = Field(default="development", description="Environment (development, testing, production)")
    
    # Server settings
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    
    # Database settings
    DATABASE_URL: str = Field(
        default="sqlite:///./agentarena.db",
        description="Database connection URL"
    )
    DATABASE_LOGGING: bool = Field(default=False, description="Enable database query logging")
    
    # JWT settings
    JWT_SECRET_KEY: str = Field(
        default="your-secret-key-here",
        description="JWT secret key for token signing"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiration in minutes")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token expiration in days")
    
    # CORS settings
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174",
        description="Comma-separated list of allowed origins"
    )
    
    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # Logging settings
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FILE: Optional[str] = Field(default=None, description="Log file path")
    
    # Playground settings
    PLAYGROUND_TIMEOUT: int = Field(default=300, description="Playground execution timeout in seconds")
    PLAYGROUND_MAX_STEPS: int = Field(default=50, description="Maximum steps for playground execution")
    USE_REAL_PLAYGROUND: bool = Field(default=False, description="Use real playground instead of mock")
    
    # WebArena settings (future use)
    WEBARENA_ENABLED: bool = Field(default=False, description="Enable WebArena integration")
    WEBARENA_BASE_URL: Optional[str] = Field(default=None, description="WebArena base URL")
    
    # LLM Provider settings
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API key")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, description="Anthropic API key")
    DEFAULT_LLM_PROVIDER: str = Field(default="mock", description="Default LLM provider to use")
    
    # Redis settings (for future use)
    REDIS_URL: Optional[str] = Field(default=None, description="Redis connection URL")
    
    # File storage settings
    UPLOAD_DIR: str = Field(default="uploads", description="Directory for file uploads")
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024, description="Maximum upload size in bytes")
    
    # Security settings
    BCRYPT_ROUNDS: int = Field(default=12, description="BCrypt hashing rounds")
    
    # Rate limiting settings
    RATE_LIMIT_REQUESTS: int = Field(default=100, description="Requests per minute limit")
    RATE_LIMIT_WINDOW: int = Field(default=60, description="Rate limit window in seconds")
    
    # Monitoring settings
    ENABLE_METRICS: bool = Field(default=True, description="Enable metrics collection")
    METRICS_PORT: int = Field(default=9090, description="Metrics server port")
    
    @field_validator('DATABASE_URL')
    @classmethod
    def validate_database_url(cls, v):
        """Validate database URL format."""
        if not v:
            raise ValueError('DATABASE_URL is required')
        return v
    
    @field_validator('JWT_SECRET_KEY')
    @classmethod
    def validate_jwt_secret(cls, v):
        """Validate JWT secret key."""
        if not v or v == "your-secret-key-here":
            if os.getenv('ENVIRONMENT') == 'production':
                raise ValueError('JWT_SECRET_KEY must be set in production')
        return v
    
    @field_validator('LOG_LEVEL')
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'LOG_LEVEL must be one of: {valid_levels}')
        return v.upper()
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return {
            "url": self.DATABASE_URL,
            "echo": self.DEBUG,
            "pool_size": 20,
            "max_overflow": 30,
            "pool_pre_ping": True,
            "pool_recycle": 3600,
        }
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()


# Environment-specific configurations
class DevelopmentSettings(Settings):
    """Development environment settings."""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


class ProductionSettings(Settings):
    """Production environment settings."""
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


class TestingSettings(Settings):
    """Testing environment settings."""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    DATABASE_URL: str = "sqlite:///./test.db"
    JWT_SECRET_KEY: str = "test-secret-key"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


def get_environment_settings() -> Settings:
    """Get environment-specific settings."""
    environment = os.getenv('ENVIRONMENT', 'development').lower()
    
    if environment == 'production':
        return ProductionSettings()
    elif environment == 'testing':
        return TestingSettings()
    else:
        return DevelopmentSettings()
