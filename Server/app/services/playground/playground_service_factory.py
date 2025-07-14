"""
PlaygroundServiceFactory - Factory for creating playground execution services.

This factory determines whether to use the real or mock playground service
based on configuration and environment availability.
"""

from typing import Optional
from ...core.logger import get_logger

from ..playground_execution_interface import IPlaygroundExecutionService

logger = get_logger(__name__)
from .mock_playground_service import MockPlaygroundService
from .real_playground_service import RealPlaygroundService
from ...core.config import settings
from ...core.exceptions import ConfigurationException


class PlaygroundServiceFactory:
    """Factory for creating playground execution services.
    
    This factory determines whether to use the real or mock playground service
    based on configuration and environment availability.
    """
    
    @staticmethod
    async def create_service() -> IPlaygroundExecutionService:
        """Create and return the appropriate playground execution service.
        
        Returns:
            IPlaygroundExecutionService: The playground execution service to use
            
        Raises:
            ConfigurationException: If there's an issue with the configuration
        """
        try:
            # Check if real playground is enabled in settings
            use_real_playground = settings.USE_REAL_PLAYGROUND
            
            logger.info(f"Creating playground service (real_mode={use_real_playground})")
            
            if use_real_playground:
                # Create real playground service
                service = RealPlaygroundService()
                
                # Check if it's healthy
                is_healthy = await service.health_check()
                
                if is_healthy:
                    logger.info("Using RealPlaygroundService - WebArena environment is healthy")
                    return service
                else:
                    logger.warning("RealPlaygroundService health check failed - falling back to mock service")
            else:
                logger.info("Real playground disabled in settings - using mock service")
            
            # Fall back to mock service
            mock_service = MockPlaygroundService()
            logger.info("Using MockPlaygroundService")
            return mock_service
            
        except Exception as e:
            logger.error(f"Error creating playground service: {str(e)}")
            logger.info("Falling back to mock service due to error")
            return MockPlaygroundService() 