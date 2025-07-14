import httpx
import json
from typing import Dict, Any, Optional, Protocol
from ...core.logger import get_logger
from ...core.config import settings
from ...core.exceptions import ConfigurationException

logger = get_logger(__name__)


class BaseLLM(Protocol):
    async def generate_response(self, prompt: str, **kwargs) -> str:
        ...
    
    async def health_check(self) -> bool:
        ...


class MockLLMClient:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        logger.info("Initialized MockLLMClient")
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        return f"Mock response to: {prompt[:50]}..."
    
    async def health_check(self) -> bool:
        return True


class OpenAIClient:
    def __init__(self, api_key: str, model: str = "gpt-4", **kwargs):
        self.api_key = api_key
        self.model = model
        self.config = kwargs
        self.base_url = settings.OPENAI_API_URL
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        logger.info(f"Initialized OpenAI client with model: {model}")
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": kwargs.get("max_tokens", 1000),
                    "temperature": kwargs.get("temperature", 0.7),
                    "stream": False
                }
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                    raise Exception(f"OpenAI API error: {response.status_code}")
        except Exception as e:
            logger.error(f"OpenAI client error: {e}")
            raise
    
    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self.headers,
                    timeout=10.0
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return False


class AnthropicClient:
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229", **kwargs):
        self.api_key = api_key
        self.model = model
        self.config = kwargs
        self.base_url = settings.CLAUDE_API_URL
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        logger.info(f"Initialized Anthropic client with model: {model}")
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "model": self.model,
                    "max_tokens": kwargs.get("max_tokens", 1000),
                    "messages": [{"role": "user", "content": prompt}]
                }
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return data["content"][0]["text"]
                else:
                    logger.error(f"Anthropic API error: {response.status_code} - {response.text}")
                    raise Exception(f"Anthropic API error: {response.status_code}")
        except Exception as e:
            logger.error(f"Anthropic client error: {e}")
            raise
    
    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self.headers,
                    timeout=10.0
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Anthropic health check failed: {e}")
            return False


class LLMClientFactory:
    def __init__(self):
        self.supported_providers = {
            "openai": OpenAIClient,
            "anthropic": AnthropicClient,
            "mock": MockLLMClient
        }
        logger.info(f"Initialized LLMClientFactory with providers: {list(self.supported_providers.keys())}")
    
    def create_client(self, agent_config: Dict[str, Any]) -> BaseLLM:
        agent_type = agent_config.get("agentType", settings.DEFAULT_LLM_PROVIDER)
        llm_api_key = agent_config.get("llmApiKey")
        provider_mapping = {
            "gpt-4": "openai",
            "gpt-3.5-turbo": "openai", 
            "claude-3": "anthropic",
            "claude-3-sonnet-20240229": "anthropic",
            "claude-3-opus-20240229": "anthropic",
            "custom": "mock"
        }
        provider = provider_mapping.get(agent_type, "mock")
        
        if provider not in self.supported_providers:
            raise ConfigurationException(f"Unsupported LLM provider: {provider}")
        
        client_class = self.supported_providers[provider]
        
        try:
            if provider == "mock":
                return client_class(agent_config)
            elif provider in ["openai", "anthropic"]:
                if not llm_api_key:
                    logger.warning(f"No API key provided for {provider}, falling back to mock client")
                    return MockLLMClient(agent_config)
                decrypted_key = self._decrypt_api_key(llm_api_key)
                return client_class(
                    api_key=decrypted_key,
                    model=agent_type,
                    **agent_config.get("llm_config", {})
                )
            else:
                raise ConfigurationException(f"Unknown provider configuration: {provider}")
        except Exception as e:
            logger.error(f"Failed to create LLM client for provider {provider}: {e}")
            logger.info("Falling back to mock client")
            return MockLLMClient(agent_config)
    
    def _decrypt_api_key(self, encrypted_key: str) -> str:
        return encrypted_key
    
    async def health_check_all_providers(self) -> Dict[str, bool]:
        health_status = {}
        for provider_name in self.supported_providers:
            try:
                test_config = {"agentType": "custom"}
                client = self.create_client(test_config)
                health_status[provider_name] = await client.health_check()
            except Exception as e:
                logger.error(f"Health check failed for provider {provider_name}: {e}")
                health_status[provider_name] = False
        return health_status
