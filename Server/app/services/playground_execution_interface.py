"""
IPlaygroundExecutionService - Interface for playground execution services.

This module defines the interface that all playground execution services must implement,
ensuring consistent behavior across different implementations (mock and real).
"""

from abc import ABC, abstractmethod
from typing import Optional
from ..schemas.playground import PlaygroundRunInput, PlaygroundRunOutput, PlaygroundStatus


class IPlaygroundExecutionService(ABC):
    """
    Interface for any service capable of executing a playground run.
    This allows for interchangeable mock and real implementations.
    """

    @abstractmethod
    async def execute_playground_run(self, run_input: PlaygroundRunInput) -> PlaygroundRunOutput:
        """
        Initiates and executes a playground run.
        """
        pass

    @abstractmethod
    async def get_execution_status(self, submission_id: str) -> Optional[PlaygroundStatus]:
        """
        Retrieves the current status of a running or completed execution.
        """
        pass

    @abstractmethod
    async def cancel_execution(self, submission_id: str) -> bool:
        """
        Cancels a currently running execution.
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Performs a health check on the execution service and its underlying components.
        """
        pass