import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from typing import Dict, Any

from app.services.playground_execution_interface import IPlaygroundExecutionService
from app.services.playground.mock_playground_service import MockPlaygroundService
from app.services.playground.real_playground_service import RealPlaygroundService
from app.schemas.playground_schemas import (
    PlaygroundRunInput, 
    PlaygroundRunOutput, 
    PlaygroundRunStatus
)
from app.models.enums import TaskDifficulty
from app.core.exceptions import PlaygroundExecutionException


class TestPlaygroundExecutionInterface:
    """Test the playground execution interface and dependency injection pattern."""

    def _create_test_playground_input(self, 
                                      submission_id: str = "test-submission-1",
                                      user_id: str = "test-user-1", 
                                      agent_id: str = "test-agent-1",
                                      task_id: str = "test-task-1",
                                      agent_configuration: Dict[str, Any] = None,
                                      environment_config: Dict[str, Any] = None) -> PlaygroundRunInput:
        """Helper method to create test playground run input with comprehensive schema."""
        
        if agent_configuration is None:
            agent_configuration = {"model": "gpt-4", "temperature": 0.7}
        if environment_config is None:
            environment_config = {"url": "http://example.com", "goal": "test"}
            
        return PlaygroundRunInput(
            submission_id=submission_id,
            user_id=user_id,
            agent_id=agent_id,
            task_id=task_id,
            agent_name="Test Agent",
            agent_description="A test agent for testing",
            agent_configuration=agent_configuration,
            agent_type="gpt-4",
            task_title="Test Task",
            task_description="A test task for testing",
            task_difficulty=TaskDifficulty.MEDIUM,
            web_arena_environment="test-environment",
            environment_config=environment_config,
            max_steps=100,
            timeout_seconds=600
        )

    def test_mock_service_implements_interface(self):
        """Test that MockPlaygroundService implements the interface."""
        service = MockPlaygroundService()
        assert isinstance(service, IPlaygroundExecutionService)

    def test_real_service_implements_interface(self):
        """Test that RealPlaygroundService implements the interface."""
        service = RealPlaygroundService()
        assert isinstance(service, IPlaygroundExecutionService)

    @pytest.mark.asyncio
    async def test_mock_service_execution_success(self):
        """Test successful execution with mock service."""
        service = MockPlaygroundService()
        
        run_input = self._create_test_playground_input()
        
        result = await service.execute_playground_run(run_input)
        
        assert isinstance(result, PlaygroundRunOutput)
        assert result.status in [PlaygroundRunStatus.COMPLETED, PlaygroundRunStatus.FAILED]
        assert result.execution_id is not None
        assert isinstance(result.steps_taken, int)
        assert result.steps_taken >= 0
        assert isinstance(result.total_time_seconds, float)
        assert result.total_time_seconds > 0

    @pytest.mark.asyncio
    async def test_mock_service_execution_with_different_configs(self):
        """Test mock service with various configuration scenarios."""
        service = MockPlaygroundService()
        
        # Test with minimal config
        run_input = self._create_test_playground_input(
            agent_configuration={},
            environment_config={}
        )
        
        result = await service.execute_playground_run(run_input)
        assert isinstance(result, PlaygroundRunOutput)
        
        # Test with complex config
        run_input = self._create_test_playground_input(
            submission_id="test-submission-2",
            agent_id="test-agent-2",
            task_id="test-task-2",
            agent_configuration={
                "model": "claude-3",
                "temperature": 0.1,
                "max_tokens": 1000,
                "tools": ["web_browser", "calculator"]
            },
            environment_config={
                "url": "http://complex-site.com",
                "goal": "Complete a complex multi-step task",
                "timeout": 300,
                "required_actions": ["login", "navigate", "submit"]
            }
        )
        
        result = await service.execute_playground_run(run_input)
        assert isinstance(result, PlaygroundRunOutput)

    @pytest.mark.asyncio
    async def test_mock_service_realistic_timing(self):
        """Test that mock service produces realistic execution times."""
        service = MockPlaygroundService()
        
        run_input = self._create_test_playground_input(
            agent_configuration={"model": "gpt-4"},
            environment_config={"complexity": "high"}
        )
        
        result = await service.execute_playground_run(run_input)
        
        # Mock service should simulate realistic timing (5-300 seconds)
        assert 5 <= result.total_time_seconds <= 300
        
        # Steps should be reasonable (1-50)
        assert 1 <= result.steps_taken <= 50

    @pytest.mark.asyncio
    async def test_mock_service_failure_scenarios(self):
        """Test that mock service can simulate various failure scenarios."""
        service = MockPlaygroundService()
        
        # Run multiple executions to potentially hit failure scenarios
        results = []
        for i in range(10):
            run_input = self._create_test_playground_input(
                submission_id=f"test-submission-{i}",
                agent_id=f"test-agent-{i}",
                task_id=f"test-task-{i}",
                agent_configuration={"model": "test"},
                environment_config={"test": True}
            )
            result = await service.execute_playground_run(run_input)
            results.append(result)
        
        # Should have some variety in results
        statuses = [r.status for r in results]
        assert len(set(statuses)) > 1, "Mock service should produce varied results"

    @pytest.mark.asyncio
    async def test_real_service_health_check(self):
        """Test that real service health check works."""
        service = RealPlaygroundService()
        
        # Mock the LLM factory and environment provisioner
        with patch('app.services.agent_core.llm_client_factory.LLMClientFactory.health_check_all_providers') as mock_llm_health, \
             patch('app.services.agent_core.environment_provisioning.EnvironmentProvisioning.health_check') as mock_env_health:
            
            # Configure mocks
            mock_llm_health.return_value = {"openai": True, "anthropic": False}
            mock_env_health.return_value = True
            
            # Test health check
            result = await service.health_check()
            assert result is True
            
            # Test with no healthy LLM providers
            mock_llm_health.return_value = {"openai": False, "anthropic": False}
            result = await service.health_check()
            assert result is False
            
            # Test with environment provisioning issue
            mock_llm_health.return_value = {"openai": True, "anthropic": False}
            mock_env_health.return_value = False
            result = await service.health_check()
            assert result is False

    @pytest.mark.asyncio
    async def test_mock_service_execution_log_details(self):
        """Test that mock service provides detailed execution logs."""
        service = MockPlaygroundService()
        
        run_input = self._create_test_playground_input(
            agent_configuration={"model": "gpt-4"},
            environment_config={"goal": "test task"}
        )
        
        result = await service.execute_playground_run(run_input)
        
        # Should have execution log
        assert result.execution_log is not None
        assert len(result.execution_log) > 0
        
        # Log should contain meaningful steps
        log_content = " ".join(result.execution_log)
        assert any(keyword in log_content.lower() for keyword in 
                  ["start", "step", "action", "complete", "result"])

    @pytest.mark.asyncio
    async def test_mock_service_concurrent_executions(self):
        """Test that mock service can handle concurrent executions."""
        service = MockPlaygroundService()
        
        async def run_execution(index: int):
            run_input = self._create_test_playground_input(
                submission_id=f"test-submission-{index}",
                agent_id=f"test-agent-{index}",
                task_id="test-task-1",
                agent_configuration={"model": "gpt-4"},
                environment_config={"test": True}
            )
            return await service.execute_playground_run(run_input)
        
        # Run 5 concurrent executions
        tasks = [run_execution(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        # Each execution should have a unique ID
        execution_ids = [r.execution_id for r in results]
        assert len(set(execution_ids)) == 5, "Execution IDs should be unique"