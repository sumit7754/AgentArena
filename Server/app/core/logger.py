import logging
import os
from typing import Optional
from loguru import logger as loguru_logger
import sys

class Logger:
    """Centralized logging system for the application."""
    
    _configured = False
    
    @classmethod
    def configure(cls, log_level: str = "INFO", log_file: Optional[str] = None) -> None:
        """Configure the logging system."""
        if cls._configured:
            return
        
        # Configure loguru
        loguru_logger.remove()  # Remove default handler
        
        # Console handler
        loguru_logger.add(
            sys.stdout,
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            colorize=True
        )
        
        # File handler if specified
        if log_file:
            loguru_logger.add(
                log_file,
                level=log_level,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
                rotation="10 MB",
                retention="1 week",
                compression="zip"
            )
        
        cls._configured = True

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given name."""
    logger = logging.getLogger(name)
    logger.setLevel(os.environ.get("LOG_LEVEL", "INFO").upper())

    # Prevent adding multiple handlers if logger is already configured
    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

# For backward compatibility and convenience
def get_loguru_logger():
    """Get the loguru logger instance."""
    return loguru_logger