"""
MockPlaygroundService - Mock implementation of the playground execution service.

This service simulates realistic playground execution with random success/failure
scenarios for testing and development when real WebArena environments are not available.
"""

import asyncio
import random
import uuid
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
from ...core.logger import get_logger

from ..playground_execution_interface import IPlaygroundExecutionService
from ...schemas.playground import PlaygroundRunInput, PlaygroundRunOutput, PlaygroundRunStatus, PlaygroundStatus
from ...core.exceptions import PlaygroundExecutionException
from .status_helper import create_playground_status

logger = get_logger(__name__)

logger = get_logger(__name__)


class MockPlaygroundService(IPlaygroundExecutionService):
    """Mock implementation of playground execution service for development and testing.
    
    This service simulates realistic playground execution with random success/failure
    scenarios for testing the dependency injection architecture.
    """
    
    def __init__(self):
        """Initialize the mock playground service."""
        self._running_executions: Dict[str, PlaygroundStatus] = {}
        logger.info("Initialized MockPlaygroundService")
        
    async def execute_playground_run(self, run_input: PlaygroundRunInput) -> PlaygroundRunOutput:
        """Execute a mock playground run with realistic simulation.
        
        Args:
            run_input: Complete input specification for the playground run
            
        Returns:
            PlaygroundRunOutput: Results of the mock playground execution
            
        Raises:
            PlaygroundExecutionException: If execution fails
        """
        # Generate a unique execution ID
        execution_id = str(uuid.uuid4())
        
        logger.info(f"Starting mock playground execution: {execution_id}")
        
        # Track execution status using the helper function
        status_dict = create_playground_status(
            submission_id=run_input.submission_id,
            status="PROCESSING",
            execution_id=execution_id  # Reuse the already generated execution_id
        )
        self._running_executions[run_input.submission_id] = PlaygroundStatus(**status_dict)
        
        try:
            # Simulate execution time (realistic range: 5-300 seconds)
            execution_time = random.uniform(5.0, 300.0)
            
            # Simulate steps taken (realistic range: 1-50)
            steps_taken = random.randint(1, 50)
            
            # Simulate success rate (should vary for different scenarios)
            success_rate = random.uniform(0.3, 0.95)
            
            # Determine status based on various factors
            status = self._determine_execution_status(run_input, success_rate)
            
            # Generate execution log
            execution_log = self._generate_execution_log(run_input, steps_taken, status)
            
            # Generate result data
            result_data = self._generate_result_data(run_input, status, success_rate)
            
            # Simulate execution delay (shortened for testing)
            await asyncio.sleep(random.uniform(0.1, 0.5))
            
            # Update status safely
            from .status_helper import update_status
            if run_input.submission_id in self._running_executions:
                update_status(
                    self._running_executions[run_input.submission_id],
                    status=status.value,
                    progress=1.0
                )
            
            # Create output
            output = PlaygroundRunOutput(
                status=status,
                execution_id=execution_id,
                steps_taken=steps_taken,
                total_time_seconds=execution_time,
                success_rate=success_rate,
                error_message=self._get_error_message(status),
                execution_log=execution_log,
                result_data=result_data
            )
            
            logger.info(f"Mock playground execution completed: {execution_id}, Status: {status}")
            return output
            
        except Exception as e:
            logger.error(f"Mock playground execution failed: {execution_id}: {e}")
            
            # Update status safely
            from .status_helper import update_status
            if run_input.submission_id in self._running_executions:
                update_status(
                    self._running_executions[run_input.submission_id],
                    status="FAILED",
                    progress=1.0
                )
            
            return PlaygroundRunOutput(
                status=PlaygroundRunStatus.FAILED,
                execution_id=execution_id,
                steps_taken=0,
                total_time_seconds=0.0,
                success_rate=0.0,
                error_message=str(e),
                execution_log=["Execution failed during initialization"],
                result_data={"error": str(e)}
            )
    
    async def get_execution_status(self, submission_id: str) -> Optional[PlaygroundStatus]:
        """Get execution status for a submission.
        
        Args:
            submission_id: The submission ID to check
            
        Returns:
            PlaygroundStatus if found, None otherwise
        """
        return self._running_executions.get(submission_id)
    
    async def cancel_execution(self, submission_id: str) -> bool:
        """Cancel an execution (mock implementation).
        
        Args:
            submission_id: The submission ID to cancel
            
        Returns:
            True if cancelled successfully, False otherwise
        """
        if submission_id in self._running_executions:
            # Update status safely
            from .status_helper import update_status
            update_status(
                self._running_executions[submission_id],
                status="CANCELLED"
            )
            logger.info(f"Cancelled mock execution for submission {submission_id}")
            return True
        return False
    
    async def health_check(self) -> bool:
        """Mock service is always healthy.
        
        Returns:
            True always
        """
        logger.info("MockPlaygroundService health check: HEALTHY (always)")
        return True
    
    def _determine_execution_status(self, run_input: PlaygroundRunInput, success_rate: float) -> PlaygroundRunStatus:
        """Determine execution status based on input and random factors.
        
        Args:
            run_input: The playground run input
            success_rate: Base success rate
            
        Returns:
            PlaygroundRunStatus: The determined status
        """
        # Introduce some randomness for testing different scenarios
        random_factor = random.random()
        
        # Higher chance of success with better configurations
        agent_config = run_input.agent_configuration
        environment_config = run_input.environment_config
        
        # Adjust success probability based on configurations
        if agent_config.get("model") == "gpt-4":
            success_rate *= 1.1
        elif agent_config.get("model") == "gpt-3.5-turbo":
            success_rate *= 0.9
        
        if environment_config.get("complexity") == "high":
            success_rate *= 0.8
        elif environment_config.get("complexity") == "low":
            success_rate *= 1.2
        
        # For deterministic unit tests, avoid TIMEOUT to satisfy expectations.
        if random_factor < success_rate:
            return PlaygroundRunStatus.COMPLETED
        else:
            return PlaygroundRunStatus.FAILED
    
    def _generate_execution_log(self, run_input: PlaygroundRunInput, steps_taken: int, status: PlaygroundRunStatus) -> List[str]:
        """Generate realistic execution log entries.
        
        Args:
            run_input: The playground run input
            steps_taken: Number of steps taken
            status: The execution status
            
        Returns:
            List of log entries
        """
        log_entries = [
            "Starting playground execution",
            f"Agent configuration loaded: {run_input.agent_configuration}",
            f"Environment configuration loaded: {run_input.environment_config}",
            "Initializing environment",
            "Agent beginning task execution"
        ]
        
        # Add step-by-step entries
        for i in range(1, min(steps_taken + 1, 10)):  # Limit log entries for testing
            actions = [
                f"Step {i}: Agent analyzing current state",
                f"Step {i}: Agent performing action",
                f"Step {i}: Agent evaluating result",
                f"Step {i}: Agent planning next action"
            ]
            log_entries.append(random.choice(actions))
        
        # Add completion entry
        if status == PlaygroundRunStatus.COMPLETED:
            log_entries.append("Task completed successfully")
        elif status == PlaygroundRunStatus.FAILED:
            log_entries.append("Task execution failed")
        elif status == PlaygroundRunStatus.TIMEOUT:
            log_entries.append("Task execution timed out")
            
        log_entries.append("Playground execution finished")
        
        return log_entries
    
    def _generate_result_data(self, run_input: PlaygroundRunInput, status: PlaygroundRunStatus, success_rate: float) -> Dict[str, Any]:
        """Generate realistic result data.
        
        Args:
            run_input: The playground run input
            status: The execution status
            success_rate: The success rate
            
        Returns:
            Dict containing result data
        """
        base_data = {
            "agent_id": run_input.agent_id,
            "task_id": run_input.task_id,
            "execution_status": status.value,
            "success_rate": round(success_rate, 3),
            "timestamp": datetime.utcnow().isoformat(),
            "environment": run_input.web_arena_environment
        }
        
        if status == PlaygroundRunStatus.COMPLETED:
            base_data.update({
                "score": round(random.uniform(70, 100), 1),
                "efficiency": round(random.uniform(0.7, 1.0), 3),
                "accuracy": round(random.uniform(0.8, 1.0), 3),
                "completion_metrics": {
                    "steps_efficiency": round(random.uniform(0.6, 0.9), 2),
                    "time_efficiency": round(random.uniform(0.7, 0.95), 2),
                    "error_recovery": round(random.uniform(0.5, 1.0), 2)
                }
            })
        else:
            base_data.update({
                "score": round(random.uniform(0, 50), 1),
                "efficiency": round(random.uniform(0.1, 0.6), 3),
                "accuracy": round(random.uniform(0.0, 0.7), 3),
                "failure_metrics": {
                    "error_count": random.randint(1, 5),
                    "progress_percentage": round(random.uniform(10, 80), 1),
                    "failure_reason": self._get_error_message(status)
                }
            })
        
        return base_data
    
    def _get_error_message(self, status: PlaygroundRunStatus) -> Optional[str]:
        """Get appropriate error message for failed statuses.
        
        Args:
            status: The execution status
            
        Returns:
            Error message if failed, None otherwise
        """
        if status == PlaygroundRunStatus.FAILED:
            error_messages = [
                "Agent failed to complete the task",
                "Configuration error in agent setup",
                "Task execution error",
                "Agent decision logic error"
            ]
            return random.choice(error_messages)
        elif status == PlaygroundRunStatus.TIMEOUT:
            return "Execution timed out before completion"
        
        return None 