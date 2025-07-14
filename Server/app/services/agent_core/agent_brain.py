"""
AgentBrain - The core reasoning and decision-making component for agents.

This component handles the agent's decision-making process within the WebArena environment.
It implements the IAgent interface for consistent behavior across all agent implementations.
"""

from typing import Dict, Any, List, Optional, TYPE_CHECKING
from ...core.logger import get_logger
from .agent_interface import IAgent
import json
import time

if TYPE_CHECKING:
    from .llm_client_factory import BaseLLM

logger = get_logger(__name__)


class AgentBrain(IAgent):
    """Core agent reasoning and decision-making logic.
    
    This class implements the IAgent interface and handles the agent's decision-making process
    within the WebArena environment. It's designed to be portable and testable
    by accepting structured data rather than ORM objects.
    """
    
    def __init__(self):
        """Initialize the agent brain."""
        self.agent_config: Dict[str, Any] = {}
        self.llm_client: Optional["BaseLLM"] = None
        self.task_details: Dict[str, Any] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.max_steps: int = 20
        self.max_tokens: int = 2000
        self.system_prompt: str = "You are a helpful assistant."
        
        logger.info("Initialized AgentBrain")

    async def initialize(self, llm_client: "BaseLLM", agent_config: Dict[str, Any], task_details: Dict[str, Any]):
        """
        Initializes the agent with an LLM client, its specific configuration, and task details.
        """
        self.llm_client = llm_client
        self.agent_config = agent_config
        self.task_details = task_details
        self.max_steps = agent_config.get("max_steps", 20)
        self.max_tokens = agent_config.get("max_output_tokens", 2000)
        self.system_prompt = agent_config.get("system_prompt", "You are a helpful assistant.")
        
        logger.info(f"Initialized AgentBrain with config: {agent_config.get('name', 'Unknown')}")

    async def decide_action(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Receives an observation from the environment and decides the next action.
        """
        if not self.llm_client:
            raise ValueError("Agent not initialized. Call initialize() first.")
        
        try:
            # Create the observation prompt
            observation_text = self._create_observation(observation)
            
            # Prepare the conversation for the LLM
            conversation = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": observation_text}
            ]
            
            # Add execution history for context
            if self.execution_history:
                history_text = self._format_execution_history()
                conversation.append({"role": "assistant", "content": f"Previous actions: {history_text}"})
            
            # Get decision from LLM
            llm_response = await self.llm_client.generate_response(
                messages=conversation,
                max_tokens=self.max_tokens
            )
            
            # Parse the action from LLM response
            action = self._parse_action(llm_response)
            
            # Add to execution history
            self.execution_history.append({
                "observation": observation,
                "action": action,
                "timestamp": time.time()
            })
            
            logger.debug(f"AgentBrain decided action: {action}")
            return action
            
        except Exception as e:
            logger.error(f"Error in decide_action: {e}")
            return {
                "action_type": "error",
                "error": str(e)
            }

    async def reset(self):
        """
        Resets the agent's internal state, preparing it for a new task run.
        """
        self.execution_history = []
        logger.info("AgentBrain state reset")
    
    def _create_task_prompt(self, task_details: Dict[str, Any]) -> str:
        """Create a task prompt for the LLM."""
        return f"""
System: {self.system_prompt}

Task: {task_details['title']}

Description: {task_details['description']}

Instructions: {task_details.get('config', {}).get('instruction', 'Complete the task as described.')}

Environment: {task_details['environment']}

Your goal is to complete this task by navigating the web environment.
You can perform actions like clicking elements, typing text, and navigating to URLs.
Analyze the current webpage and decide on the best action to take next.
"""
    
    def _create_observation(self, page_content: Dict[str, Any]) -> str:
        """Create an observation of the current page state."""
        return f"""
Current webpage content:
URL: {page_content.get('url', 'unknown')}
Title: {page_content.get('title', 'unknown')}

Page Content:
{page_content.get('content_text', 'No content available')}

Available Elements:
- Links: {', '.join(page_content.get('elements', {}).get('links', []))}
- Buttons: {', '.join(page_content.get('elements', {}).get('buttons', []))}
- Inputs: {', '.join(page_content.get('elements', {}).get('inputs', []))}
"""
    
    def _parse_action(self, llm_response: str) -> Dict[str, Any]:
        """Parse the LLM response into an action."""
        # Try to extract structured action
        try:
            # Look for JSON-like structure
            if "{" in llm_response and "}" in llm_response:
                start_idx = llm_response.find("{")
                end_idx = llm_response.rfind("}") + 1
                json_str = llm_response[start_idx:end_idx]
                action = json.loads(json_str)
                if "type" in action:
                    return action
        except Exception:
            pass
        
        # Fallback: Heuristic parsing
        action_type = None
        params = {}
        
        if "click" in llm_response.lower():
            action_type = "click"
            # Try to extract selector
            lines = llm_response.split("\n")
            for line in lines:
                if "click" in line.lower() and "#" in line:
                    selector = line.split("#")[1].split(" ")[0].strip().strip(".,;")
                    params["selector"] = f"#{selector}"
                    break
        
        elif "type" in llm_response.lower():
            action_type = "type"
            # Try to extract selector and text
            lines = llm_response.split("\n")
            for line in lines:
                if "type" in line.lower() and "into" in line.lower():
                    parts = line.lower().split("into")
                    if len(parts) >= 2 and "#" in parts[1]:
                        selector = parts[1].split("#")[1].split(" ")[0].strip().strip(".,;")
                        params["selector"] = f"#{selector}"
                    
                    text_parts = parts[0].split("type")
                    if len(text_parts) >= 2:
                        text = text_parts[1].strip().strip('"\'').strip()
                        params["text"] = text
                    break
        
        elif "navigate" in llm_response.lower() or "go to" in llm_response.lower():
            action_type = "navigate"
            # Try to extract URL
            lines = llm_response.split("\n")
            for line in lines:
                if ("navigate" in line.lower() or "go to" in line.lower()) and "http" in line:
                    parts = line.split("http")
                    if len(parts) >= 2:
                        url = "http" + parts[1].split(" ")[0].strip().strip(".,;")
                        params["url"] = url
                        break
        
        elif "complete" in llm_response.lower() and "task" in llm_response.lower():
            action_type = "task_complete"
            params["reason"] = "Task completed successfully"
        
        else:
            # Default to wait action
            action_type = "wait"
            params["milliseconds"] = 1000
        
        return {
            "type": action_type,
            "description": llm_response[:100] + "..." if len(llm_response) > 100 else llm_response,
            **params
        }
    
    def _format_execution_history(self) -> str:
        """Formats the execution history for LLM context."""
        history_text = ""
        for i, step in enumerate(self.execution_history):
            observation_text = self._create_observation(step["observation"])
            action_text = json.dumps(step["action"], indent=2)
            history_text += f"Step {i+1}: Observation: {observation_text}\nAction: {action_text}\n"
        return history_text.strip()
    
    def _analyze_webpage(self, webpage_content: str) -> Dict[str, Any]:
        """Analyze webpage content and extract relevant information."""
        # Simple analysis for now
        return {
            "text_length": len(webpage_content),
            "has_forms": "form" in webpage_content.lower(),
            "has_links": "href" in webpage_content.lower(),
            "has_buttons": "button" in webpage_content.lower()
        }
    
    def _decide_next_action(self, current_state: Dict[str, Any]) -> Dict[str, str]:
        """Use LLM to decide the next action based on current state."""
        # This is handled in the execute_task method now
        pass