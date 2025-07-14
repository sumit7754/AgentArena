import sys
from loguru import logger
from .config import settings


def configure_logging():
    """Configure structured logging with Loguru."""
    
    # Remove default logger
    logger.remove()
    
    # Add console logger with structured format
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True,
    )
    
    # Add file logger for production
    if settings.ENVIRONMENT == "production":
        logger.add(
            "logs/app.log",
            rotation="10 MB",
            retention="30 days",
            level=settings.LOG_LEVEL,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            serialize=True  # JSON format for production
        )
    
    return logger


# Configure logging when module is imported
configure_logging()