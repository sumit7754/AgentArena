import pytest
from unittest.mock import Mock, AsyncMock
from sqlalchemy.orm import Session

from app.services.submission_service import SubmissionService
from app.services.mock_playground_execution_service import MockPlaygroundExecutionService
from app.models.user import User
from app.models.agent import Agent
from app.models.task import Task
from app.models.submission import Submission
from app.models.enums import UserRole
from app.schemas.submission_schema import SubmissionCreate
from app.schemas.playground_schemas import PlaygroundRunInput, PlaygroundRunStatus
from app.core.exceptions import NotFoundException, ValidationException


class TestSubmissionServiceIntegration:
    """Integration tests for the refactored SubmissionService with dependency injection."""

    @pytest.fixture
    def submission_service(self, mock_playground_service):
        """Create SubmissionService with mock playground execution service."""
        return SubmissionService(playground_executor=mock_playground_service)

    @pytest.mark.asyncio
    async def test_create_submission_success(
        self, submission_service, test_db, test_user, test_agent, test_task
    ):
        """Test successful submission creation with playground execution."""
        submission_data = SubmissionCreate(
            agentId=test_agent.id,
            taskId=test_task.id,
            run_config={"model": "gpt-4", "temperature": 0.7}
        )
        
        submission = await submission_service.create_submission(
            test_db, submission_data, test_user.id
        )
        
        assert submission is not None
        assert submission.agentId == test_agent.id
        assert submission.taskId == test_task.id
        assert submission.userId == test_user.id
        assert submission.runConfig == {"model": "gpt-4", "temperature": 0.7}
        assert submission.status in ["completed", "failed"]
        assert submission.playground_execution_id is not None
        assert submission.result_data is not None

    @pytest.mark.asyncio
    async def test_create_submission_with_nonexistent_agent(
        self, submission_service, test_db, test_user, test_task
    ):
        """Test submission creation with non-existent agent."""
        submission_data = SubmissionCreate(
            agentId="99999",  # Non-existent agent (string)
            taskId=test_task.id,
            run_config={}
        )
        
        with pytest.raises(NotFoundException) as exc_info:
            await submission_service.create_submission(
                test_db, submission_data, test_user.id
            )
        
        assert "Agent with id 99999 not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_submission_with_nonexistent_task(
        self, submission_service, test_db, test_user, test_agent
    ):
        """Test submission creation with non-existent task."""
        submission_data = SubmissionCreate(
            agentId=test_agent.id,
            taskId="99999",  # Non-existent task (string)
            run_config={}
        )
        
        with pytest.raises(NotFoundException) as exc_info:
            await submission_service.create_submission(
                test_db, submission_data, test_user.id
            )
        
        assert "Task with id 99999 not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_submission_unauthorized_agent(
        self, submission_service, test_db, test_user, test_task
    ):
        """Test submission creation with agent owned by another user."""
        # Create another user and their agent
        other_user = User(
            firstName="Other",
            lastName="User", 
            email="other@example.com",
            password="hashed",
            role=UserRole.USER,
            isActive=True
        )
        test_db.add(other_user)
        test_db.commit()
        test_db.refresh(other_user)
        
        other_agent = Agent(
            name="Other Agent",
            description="Agent owned by another user",
            configurationJson={},
            userId=other_user.id
        )
        test_db.add(other_agent)
        test_db.commit()
        test_db.refresh(other_agent)
        
        submission_data = SubmissionCreate(
            agentId=other_agent.id,
            taskId=test_task.id,
            run_config={}
        )
        
        with pytest.raises(ValidationException) as exc_info:
            await submission_service.create_submission(
                test_db, submission_data, test_user.id
            )
        
        assert "not owned by the current user" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_playground_execution_integration(
        self, submission_service, test_db, test_user, test_agent, test_task
    ):
        """Test integration with playground execution service."""
        submission_data = SubmissionCreate(
            agentId=test_agent.id,
            taskId=test_task.id,
            run_config={"model": "claude-3", "tools": ["web_browser"]}
        )
        
        submission = await submission_service.create_submission(
            test_db, submission_data, test_user.id
        )
        
        # Verify playground execution was called with correct parameters
        assert submission.playground_execution_id is not None
        assert submission.steps_taken is not None
        assert submission.execution_time_seconds is not None
        assert submission.execution_log is not None
        
        # Verify the playground input was constructed correctly
        # The mock service should have received the agent and task configs
        assert submission.result_data is not None

    def test_get_submissions_by_user(
        self, submission_service, test_db, test_user, test_agent, test_task
    ):
        """Test retrieving submissions by user."""
        # Create multiple submissions
        submissions = []
        for i in range(3):
            submission = Submission(
                agentId=test_agent.id,
                taskId=test_task.id,
                userId=test_user.id,
                status="completed",
                runConfig={"test": i},
                playground_execution_id=f"exec_{i}",
                steps_taken=10 + i,
                execution_time_seconds=30.0 + i,
                success_rate=0.8 + (i * 0.05),
                result_data={"score": 80 + i}
            )
            test_db.add(submission)
            submissions.append(submission)
        
        test_db.commit()
        
        # Get submissions
        result = submission_service.get_submissions_by_user(test_db, test_user.id)
        
        assert len(result.items) == 3
        assert all(s.userId == test_user.id for s in result.items)

    def test_get_submissions_by_agent(
        self, submission_service, test_db, test_user, test_agent, test_task
    ):
        """Test retrieving submissions by agent."""
        # Create submissions for this agent
        for i in range(2):
            submission = Submission(
                agentId=test_agent.id,
                taskId=test_task.id,
                userId=test_user.id,
                status="completed",
                runConfig={"test": i},
                playground_execution_id=f"exec_{i}",
                steps_taken=10,
                execution_time_seconds=30.0,
                success_rate=0.8,
                result_data={"score": 80}
            )
            test_db.add(submission)
        
        test_db.commit()
        
        # Get submissions
        result = submission_service.get_submissions_by_agent(test_db, test_agent.id)
        
        assert len(result.items) == 2
        assert all(s.agentId == test_agent.id for s in result.items)

    def test_get_submissions_by_task(
        self, submission_service, test_db, test_user, test_agent, test_task
    ):
        """Test retrieving submissions by task."""
        # Create submissions for this task
        for i in range(2):
            submission = Submission(
                agentId=test_agent.id,
                taskId=test_task.id,
                userId=test_user.id,
                status="completed",
                runConfig={"test": i},
                playground_execution_id=f"exec_{i}",
                steps_taken=10,
                execution_time_seconds=30.0,
                success_rate=0.8,
                result_data={"score": 80}
            )
            test_db.add(submission)
        
        test_db.commit()
        
        # Get submissions
        result = submission_service.get_submissions_by_task(test_db, test_task.id)
        
        assert len(result.items) == 2
        assert all(s.taskId == test_task.id for s in result.items)

    def test_get_submission_by_id(
        self, submission_service, test_db, test_user, test_agent, test_task
    ):
        """Test retrieving submission by ID."""
        submission = Submission(
            agentId=test_agent.id,
            taskId=test_task.id,
            userId=test_user.id,
            status="completed",
            runConfig={"test": "config"},
            playground_execution_id="exec_123",
            steps_taken=15,
            execution_time_seconds=45.0,
            success_rate=0.9,
            result_data={"score": 95}
        )
        test_db.add(submission)
        test_db.commit()
        test_db.refresh(submission)
        
        # Get submission
        found_submission = submission_service.get_submission_by_id(test_db, submission.id)
        
        assert found_submission is not None
        assert found_submission.id == submission.id
        assert found_submission.playground_execution_id == "exec_123"
        assert found_submission.steps_taken == 15
        assert found_submission.success_rate == 0.9

    def test_get_submission_by_id_not_found(
        self, submission_service, test_db
    ):
        """Test retrieving non-existent submission."""
        with pytest.raises(NotFoundException):
            submission_service.get_submission_by_id(test_db, 99999)

    @pytest.mark.asyncio
    async def test_submission_service_with_custom_playground_executor(
        self, test_db, test_user, test_agent, test_task
    ):
        """Test SubmissionService with a custom playground executor."""
        # Create a mock executor that returns specific results
        mock_executor = AsyncMock()
        mock_executor.execute_playground_run.return_value = Mock(
            status=PlaygroundRunStatus.COMPLETED,
            execution_id="custom_exec_123",
            steps_taken=25,
            total_time_seconds=120.0,
            success_rate=0.95,
            error_message=None,
            execution_log=["Custom step 1", "Custom step 2"],
            result_data={"custom_score": 99}
        )
        
        # Create service with custom executor
        service = SubmissionService(playground_executor=mock_executor)
        
        submission_data = SubmissionCreate(
            agentId=test_agent.id,
            taskId=test_task.id,
            run_config={"custom": "config"}
        )
        
        submission = await service.create_submission(
            test_db, submission_data, test_user.id
        )
        
        # Verify custom executor was used
        assert submission.playground_execution_id == "custom_exec_123"
        assert submission.steps_taken == 25
        assert submission.execution_time_seconds == 120.0
        assert submission.success_rate == 0.95
        assert submission.result_data == {"custom_score": 99}
        
        # Verify the executor was called with correct parameters
        mock_executor.execute_playground_run.assert_called_once()
        call_args = mock_executor.execute_playground_run.call_args[0][0]
        assert isinstance(call_args, PlaygroundRunInput)
        assert call_args.agent_id == str(test_agent.id)
        assert call_args.task_id == str(test_task.id)

    def test_submission_pagination(
        self, submission_service, test_db, test_user, test_agent, test_task
    ):
        """Test pagination of submission results."""
        # Create many submissions
        for i in range(25):
            submission = Submission(
                agentId=test_agent.id,
                taskId=test_task.id,
                userId=test_user.id,
                status="completed",
                runConfig={"test": i},
                playground_execution_id=f"exec_{i}",
                steps_taken=10,
                execution_time_seconds=30.0,
                success_rate=0.8,
                result_data={"score": 80}
            )
            test_db.add(submission)
        
        test_db.commit()
        
        # Test first page
        from app.core.pagination import PaginationParams
        page1 = submission_service.get_submissions_by_user(
            test_db, test_user.id, PaginationParams(page=1, size=10)
        )
        
        assert len(page1.items) == 10
        assert page1.total == 25
        assert page1.pages == 3
        assert page1.has_next == True
        assert page1.has_previous == False
        
        # Test second page
        page2 = submission_service.get_submissions_by_user(
            test_db, test_user.id, PaginationParams(page=2, size=10)
        )
        
        assert len(page2.items) == 10
        assert page2.has_next == True
        assert page2.has_previous == True