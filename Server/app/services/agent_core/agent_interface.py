# Server/app/services/agent_core/agent_interface.py
from abc import ABC, abstractmethod
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .llm_client_factory import BaseLLM

class IAgent(ABC):
    """
    Interface (Abstract Base Class) for all AI Agents.
    Any custom agent provided by users must implement this interface.
    """

    @abstractmethod
    async def initialize(self, llm_client: "BaseLLM", agent_config: Dict[str, Any], task_details: Dict[str, Any]):
        """
        Initializes the agent with an LLM client, its specific configuration, and task details.
        """
        pass

    @abstractmethod
    async def decide_action(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Receives an observation from the environment and decides the next action.
        """
        pass

    @abstractmethod
    async def reset(self):
        """
        Resets the agent's internal state, preparing it for a new task run.
        """
        pass