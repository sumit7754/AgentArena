"""
RealPlaygroundService - Implementation of the playground execution service using WebArena.

This service handles the execution of agents in the WebArena environment,
integrating with the agent_core components for LLM interaction and browser automation.
"""

import asyncio
import uuid
import time
from typing import Optional, Dict, Any
from ...core.logger import get_logger

from ..playground_execution_interface import IPlaygroundExecutionService
from ...schemas.playground import PlaygroundRunInput, PlaygroundRunOutput, PlaygroundRunStatus, PlaygroundStatus
from ...core.exceptions import PlaygroundExecutionException
from .status_helper import create_playground_status
from ..agent_core.llm_client_factory import LLMClientFactory, BaseLLM
from ..agent_core.agent_brain import AgentBrain
from ..agent_core.web_browser_automation import WebBrowserAutomation
from ..agent_core.environment_provisioning import EnvironmentProvisioning
from ..agent_core.agent_interface import IAgent

logger = get_logger(__name__)


class RealPlaygroundService(IPlaygroundExecutionService):
    """Real implementation of playground execution service using WebArena.
    
    This service orchestrates the actual WebArena environment execution
    using the components in the agent_core/ directory.
    """
    
    def __init__(self):
        """Initialize the RealPlaygroundService with required components."""
        self._running_executions: Dict[str, PlaygroundStatus] = {}
        self._llm_factory = LLMClientFactory()
        self._environment_provisioner = EnvironmentProvisioning()
        logger.info("Initialized RealPlaygroundService")
    
    async def execute_playground_run(self, run_input: PlaygroundRunInput) -> PlaygroundRunOutput:
        """Execute a playground run with real components.
        
        This method orchestrates the execution of a playground run using real components,
        including the agent brain and environment.
        
        Args:
            run_input: Complete input specification for the playground run
            
        Returns:
            PlaygroundRunOutput: Results of the playground execution
            
        Raises:
            PlaygroundExecutionException: If execution fails
        """
        # Generate a unique execution ID
        execution_id = str(uuid.uuid4())
        
        logger.info(f"Starting real playground execution: {execution_id} for submission {run_input.submission_id}")
        
        # Track execution status using the helper function
        status_dict = create_playground_status(
            submission_id=run_input.submission_id,
            status="PROCESSING",
            execution_id=execution_id  # Reuse the already generated execution_id
        )
        self._running_executions[run_input.submission_id] = PlaygroundStatus(**status_dict)
        
        try:
            # Create LLM client
            agent_config = run_input.agent_configuration
            llm_client = self._llm_factory.create_client(agent_config)
            
            # Create and initialize agent brain
            agent_brain = AgentBrain()
            
            # Prepare task details from run_input
            task_details = {
                "title": run_input.task_title,
                "description": run_input.task_description,
                "difficulty": run_input.task_difficulty,
                "configuration": run_input.task_configuration
            }
            
            await agent_brain.initialize(llm_client, agent_config, task_details)
            
            # Create environment
            environment = await self._environment_provisioner.create_environment(
                run_input.web_arena_environment, 
                run_input.environment_config
            )
            
            # Execute task with components using the new orchestration pattern
            result = await self._orchestrate_agent_execution(execution_id, run_input, agent_brain, environment)
            
            # Update status safely
            from .status_helper import update_status
            if run_input.submission_id in self._running_executions:
                update_status(
                    self._running_executions[run_input.submission_id],
                    status=result.status.value,
                    progress=1.0,
                    progress_percentage=100.0
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Real playground execution failed: {execution_id}: {str(e)}")
            
            # Update status safely
            from .status_helper import update_status
            if run_input.submission_id in self._running_executions:
                update_status(
                    self._running_executions[run_input.submission_id],
                    status="FAILED",
                    progress=1.0,
                    error_message=str(e)
                )
            
            # Return failure output
            return PlaygroundRunOutput(
                status=PlaygroundRunStatus.FAILED,
                execution_id=execution_id,
                steps_taken=0,
                total_time_seconds=0,
                success_rate=0,
                error_message=f"Execution failed: {str(e)}",
                execution_log=["Error during execution", str(e)],
                result_data={"error": str(e)}
            )
    
    async def _orchestrate_agent_execution(self, execution_id: str, run_input: PlaygroundRunInput, agent_instance: IAgent, environment: Dict[str, Any]) -> PlaygroundRunOutput:
        """Orchestrate the main agent execution loop.
        
        This is the main loop that:
        - Initializes WebBrowserAutomation and agent
        - Manages the while steps_taken < max_steps loop
        - Gets observation from WebBrowserAutomation
        - Passes observation to agent_instance.decide_action()
        - Passes the decided action to web_browser_automation.execute_action()
        - Performs _check_task_completion_criteria after each step
        - Handles finish_task action from the agent
        - Updates PlaygroundStatus (progress, status, logs)
        - Handles error cases and ensures browser/agent cleanup
        
        Args:
            execution_id: Unique ID for this execution
            run_input: Complete input specification for the playground run
            agent_instance: The initialized agent instance implementing IAgent
            environment: The initialized environment
            
        Returns:
            PlaygroundRunOutput containing execution results
            
        Raises:
            PlaygroundExecutionException: If execution fails
        """
        start_time = time.time()
        steps_taken = 0
        execution_log = []
        success = False
        max_steps = run_input.agent_configuration.get("max_steps", 20)
        
        # Initialize browser automation
        web_browser_automation = WebBrowserAutomation(environment)
        
        try:
            logger.info(f"Starting agent execution orchestration for {execution_id}")
            execution_log.append(f"Task initialized: {run_input.task_title}")
            
            # Navigate to initial URL from environment config
            initial_url = run_input.environment_config.get("url", "https://example.com")
            await web_browser_automation.navigate(initial_url)
            execution_log.append(f"Navigated to initial URL: {initial_url}")
            
            # Main execution loop
            while steps_taken < max_steps:
                steps_taken += 1
                
                # Update progress
                progress = steps_taken / max_steps
                self._update_execution_status(run_input.submission_id, progress, steps_taken, f"Executing step {steps_taken}")
                
                # Get observation from browser automation
                observation = await web_browser_automation.get_page_content()
                
                # Get action decision from agent
                action = await agent_instance.decide_action(observation)
                execution_log.append(f"Step {steps_taken}: {action.get('action_type', 'unknown')} - {action.get('description', '')}")
                
                # Handle error action
                if action.get("action_type") == "error":
                    error_msg = action.get("error", "Unknown error")
                    execution_log.append(f"Agent error: {error_msg}")
                    break
                
                # Handle finish task action
                if action.get("action_type") == "finish_task":
                    success = True
                    execution_log.append("Task completed successfully!")
                    break
                
                # Execute action using browser automation
                action_result = await self._execute_action(web_browser_automation, action)
                
                # Check task completion criteria
                if self._check_task_completion_criteria(run_input.task_configuration, observation):
                    success = True
                    execution_log.append("Task completed successfully!")
                    break
                
                # Small delay between actions
                await asyncio.sleep(0.5)
            
            # Final cleanup
            await web_browser_automation.close()
            await agent_instance.reset()
            
            # Calculate metrics
            execution_time = time.time() - start_time
            success_rate = 1.0 if success else (0.5 if steps_taken == max_steps else 0.0)
            
            # Return results
            return PlaygroundRunOutput(
                status=PlaygroundRunStatus.COMPLETED if success else PlaygroundRunStatus.FAILED,
                execution_id=execution_id,
                steps_taken=steps_taken,
                total_time_seconds=execution_time,
                success_rate=success_rate,
                error_message=None if success else "Task not completed within step limit",
                execution_log=execution_log,
                result_data={
                    "browser_state": web_browser_automation.get_browser_state(),
                    "action_history": web_browser_automation.get_action_history()
                }
            )
            
        except Exception as e:
            logger.error(f"Error during agent execution orchestration: {str(e)}")
            
            # Ensure cleanup
            try:
                await web_browser_automation.close()
                await agent_instance.reset()
            except Exception:
                pass
            
            execution_time = time.time() - start_time
            return PlaygroundRunOutput(
                status=PlaygroundRunStatus.FAILED,
                execution_id=execution_id,
                steps_taken=steps_taken,
                total_time_seconds=execution_time,
                success_rate=0.0,
                error_message=str(e),
                execution_log=execution_log + [f"Error: {str(e)}"],
                result_data={"error": str(e)}
            )
    
    def _update_execution_status(self, submission_id: str, progress: float, current_step: int, last_action: str):
        """Update the execution status for progress tracking."""
        if submission_id in self._running_executions:
            status = self._running_executions[submission_id]
            # Use the safe update method
            from .status_helper import update_status
            update_status(
                status, 
                progress=progress,
                progress_percentage=int(progress * 100),
                current_step=current_step,
                last_action=last_action
            )
    
    async def _execute_action(self, browser: WebBrowserAutomation, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action using the browser automation."""
        action_type = action.get("action_type", "")
        
        if action_type == "click":
            selector = action.get("selector", "")
            return await browser.click(selector)
        
        elif action_type == "type":
            selector = action.get("selector", "")
            text = action.get("text", "")
            return await browser.type(selector, text)
        
        elif action_type == "navigate":
            url = action.get("url", "")
            return await browser.navigate(url)
        
        elif action_type == "select":
            selector = action.get("selector", "")
            value = action.get("value", "")
            return await browser.select(selector, value)
        
        elif action_type == "wait":
            selector = action.get("selector")
            if selector:
                return await browser.wait_for_element(selector, action.get("timeout", 5000))
            else:
                await asyncio.sleep(action.get("timeout", 1000) / 1000)
                return {"success": True, "action": "wait"}
        
        else:
            logger.warning(f"Unknown action type: {action_type}")
            return {"success": False, "error": f"Unknown action type: {action_type}"}
    
    def _check_task_completion_criteria(self, task_config: Dict[str, Any], observation: Dict[str, Any]) -> bool:
        """Check if the task has been completed based on completion criteria."""
        success_criteria = task_config.get("success_criteria", [])
        
        if not success_criteria:
            return False
        
        content_text = observation.get("content_text", "").lower()
        criteria_met = 0
        
        for criterion in success_criteria:
            criterion_lower = criterion.lower()
            if criterion_lower in content_text:
                criteria_met += 1
        
        # Task is complete if at least half of the criteria are met
        return criteria_met >= len(success_criteria) / 2
    
    def _simulate_execution_result(self, run_input: PlaygroundRunInput) -> Dict[str, Any]:
        """Simulate execution result when using mock components.
        
        This provides realistic simulation for when API keys aren't provided
        or when the environment is mocked.
        
        Args:
            run_input: The playground run input
            
        Returns:
            Dict containing simulated execution results
        """
        # Calculate difficulty factor based on task difficulty
        difficulty_factor = {
            "EASY": 0.8,
            "MEDIUM": 0.6,
            "HARD": 0.4
        }.get(run_input.task_difficulty.value, 0.5)
        
        # Calculate steps and success rate
        steps_taken = int(5 + (1 - difficulty_factor) * 20)
        success_rate = difficulty_factor + 0.1
        execution_time = 10.0 + (steps_taken * 2.5)  # Realistic timing
        
        # Generate execution log
        execution_log = [
            f"[Mock] Initialized agent: {run_input.agent_name}",
            f"[Mock] Analyzing task: {run_input.task_title}",
            f"[Mock] Executing in environment: {run_input.web_arena_environment}"
        ]
        
        # Add some steps to the log
        for i in range(1, min(steps_taken, 8)):
            execution_log.append(f"[Mock] Step {i}: Executing action in {run_input.web_arena_environment}")
        
        # Add completion message
        execution_log.append(f"[Mock] Completed with {steps_taken} steps and {success_rate:.2f} success rate")
        
        # Determine status
        status = PlaygroundRunStatus.COMPLETED if success_rate > 0.5 else PlaygroundRunStatus.FAILED
        
        # Return simulated results
        return {
            "status": status.value,
            "steps_taken": steps_taken,
            "success_rate": success_rate,
            "execution_time": execution_time,
            "execution_log": execution_log,
            "result_data": {
                "mock_mode": True,
                "task_completed": success_rate > 0.5,
                "agent_name": run_input.agent_name,
                "task_title": run_input.task_title,
                "environment": run_input.web_arena_environment
            }
        }
    
    async def get_execution_status(self, submission_id: str) -> Optional[PlaygroundStatus]:
        """Get execution status for a submission.
        
        Args:
            submission_id: The submission ID to check
            
        Returns:
            PlaygroundStatus if found, None otherwise
        """
        return self._running_executions.get(submission_id)
    
    async def cancel_execution(self, submission_id: str) -> bool:
        """Cancel an execution.
        
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
            logger.info(f"Cancelled execution for submission {submission_id}")
            return True
        return False
    
    async def health_check(self) -> bool:
        """Check if the playground service is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            # Check LLM service health
            llm_health = await self._llm_factory.health_check_all_providers()
            
            # Check environment provisioning health
            env_health = await self._environment_provisioner.health_check()
            
            # Service is healthy if at least one LLM provider is available
            # and environment provisioning is working
            is_healthy = any(llm_health.values()) and env_health
            
            if is_healthy:
                logger.info("RealPlaygroundService health check: HEALTHY")
            else:
                logger.warning(f"RealPlaygroundService health check: UNHEALTHY (llm_providers={llm_health}, env={env_health})")
                
            return is_healthy
            
        except Exception as e:
            logger.error(f"RealPlaygroundService health check failed: {e}")
            return False 