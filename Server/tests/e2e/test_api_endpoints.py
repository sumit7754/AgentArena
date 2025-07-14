import pytest
import json
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.models.user import User
from app.models.agent import Agent
from app.models.task import Task
from app.models.submission import Submission


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint returns correct status."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["app_name"] == "AgentArena"
        assert data["environment"] == "development"
        assert data["features"]["playground_execution"] == "mock"
        assert data["features"]["dependency_injection"] == True


class TestAuthenticationEndpoints:
    """Test authentication API endpoints."""

    def test_register_new_user(self, client):
        """Test user registration."""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/v1/register", json=user_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert data["is_active"] == True
        assert "id" in data
        assert "hashed_password" not in data  # Should not expose password

    def test_register_duplicate_username(self, client, test_user):
        """Test registration with duplicate username."""
        user_data = {
            "username": test_user.username,
            "email": "different@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/v1/register", json=user_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_login_success(self, client, test_user):
        """Test successful login."""
        login_data = {
            "username": test_user.username,
            "password": "testpassword"
        }
        
        response = client.post("/api/v1/token", data=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password."""
        login_data = {
            "username": test_user.username,
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/token", data=login_data)
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        login_data = {
            "username": "nonexistent",
            "password": "password"
        }
        
        response = client.post("/api/v1/token", data=login_data)
        assert response.status_code == 401

    def test_me_endpoint_authenticated(self, client, authenticated_headers, test_user):
        """Test /me endpoint with authentication."""
        response = client.get("/api/v1/me", headers=authenticated_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == test_user.id
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email

    def test_me_endpoint_unauthenticated(self, client):
        """Test /me endpoint without authentication."""
        response = client.get("/api/v1/me")
        assert response.status_code == 401


class TestAgentEndpoints:
    """Test agent management API endpoints."""

    def test_create_agent(self, client, authenticated_headers):
        """Test agent creation."""
        agent_data = {
            "name": "Test Agent",
            "description": "A test agent for API testing",
            "config": {
                "model": "gpt-4",
                "temperature": 0.7,
                "tools": ["web_browser"]
            }
        }
        
        response = client.post(
            "/api/v1/agents", 
            json=agent_data, 
            headers=authenticated_headers
        )
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == "Test Agent"
        assert data["description"] == "A test agent for API testing"
        assert data["config"]["model"] == "gpt-4"
        assert "id" in data
        assert "created_at" in data

    def test_create_agent_unauthenticated(self, client):
        """Test agent creation without authentication."""
        agent_data = {
            "name": "Unauthorized Agent",
            "description": "Should not be created",
            "config": {}
        }
        
        response = client.post("/api/v1/agents", json=agent_data)
        assert response.status_code == 401

    def test_get_agents(self, client, authenticated_headers, test_agent):
        """Test retrieving agents."""
        response = client.get("/api/v1/agents", headers=authenticated_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1
        
        # Find our test agent
        test_agent_data = next(
            (agent for agent in data["items"] if agent["id"] == test_agent.id), 
            None
        )
        assert test_agent_data is not None
        assert test_agent_data["name"] == test_agent.name

    def test_get_agent_by_id(self, client, authenticated_headers, test_agent):
        """Test retrieving specific agent."""
        response = client.get(
            f"/api/v1/agents/{test_agent.id}", 
            headers=authenticated_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == test_agent.id
        assert data["name"] == test_agent.name
        assert data["description"] == test_agent.description

    def test_get_agent_not_found(self, client, authenticated_headers):
        """Test retrieving non-existent agent."""
        response = client.get("/api/v1/agents/99999", headers=authenticated_headers)
        assert response.status_code == 404


class TestTaskEndpoints:
    """Test task management API endpoints."""

    def test_create_task(self, client, authenticated_headers):
        """Test task creation."""
        task_data = {
            "title": "Test Task",
            "description": "A test task for API testing",
            "difficulty": "medium",
            "category": "web_navigation",
            "task_config": {
                "url": "http://example.com",
                "goal": "Navigate to the contact page",
                "success_criteria": ["find contact form", "fill form"]
            }
        }
        
        response = client.post(
            "/api/v1/tasks", 
            json=task_data, 
            headers=authenticated_headers
        )
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["difficulty"] == "medium"
        assert data["category"] == "web_navigation"
        assert data["task_config"]["url"] == "http://example.com"

    def test_get_tasks(self, client, authenticated_headers, test_task):
        """Test retrieving tasks."""
        response = client.get("/api/v1/tasks", headers=authenticated_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1

    def test_get_task_by_id(self, client, authenticated_headers, test_task):
        """Test retrieving specific task."""
        response = client.get(
            f"/api/v1/tasks/{test_task.id}", 
            headers=authenticated_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == test_task.id
        assert data["title"] == test_task.title


class TestSubmissionEndpoints:
    """Test submission API endpoints with playground execution."""

    @pytest.mark.asyncio
    async def test_create_submission(
        self, async_client, authenticated_headers, test_agent, test_task, 
        override_playground_service
    ):
        """Test submission creation with playground execution."""
        submission_data = {
            "agent_id": test_agent.id,
            "task_id": test_task.id,
            "run_config": {
                "model": "gpt-4",
                "temperature": 0.8,
                "max_steps": 50
            }
        }
        
        response = await async_client.post(
            "/api/v1/submissions",
            json=submission_data,
            headers=authenticated_headers
        )
        assert response.status_code == 201
        
        data = response.json()
        assert data["agent_id"] == test_agent.id
        assert data["task_id"] == test_task.id
        assert data["status"] in ["completed", "failed"]
        assert data["playground_execution_id"] is not None
        assert data["steps_taken"] is not None
        assert data["execution_time_seconds"] is not None
        assert data["result_data"] is not None

    def test_create_submission_nonexistent_agent(
        self, client, authenticated_headers, test_task
    ):
        """Test submission creation with non-existent agent."""
        submission_data = {
            "agent_id": 99999,
            "task_id": test_task.id,
            "run_config": {}
        }
        
        response = client.post(
            "/api/v1/submissions",
            json=submission_data,
            headers=authenticated_headers
        )
        assert response.status_code == 404
        assert "Agent not found" in response.json()["message"]

    def test_get_submissions(
        self, client, authenticated_headers, test_user, test_agent, test_task, test_db
    ):
        """Test retrieving submissions."""
        # Create a test submission
        submission = Submission(
            agent_id=test_agent.id,
            task_id=test_task.id,
            user_id=test_user.id,
            status="completed",
            run_config={"test": True},
            playground_execution_id="test_exec_123",
            steps_taken=10,
            execution_time_seconds=30.0,
            success_rate=0.8,
            result_data={"score": 85}
        )
        test_db.add(submission)
        test_db.commit()
        
        response = client.get("/api/v1/submissions", headers=authenticated_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1

    def test_get_submission_by_id(
        self, client, authenticated_headers, test_user, test_agent, test_task, test_db
    ):
        """Test retrieving specific submission."""
        submission = Submission(
            agent_id=test_agent.id,
            task_id=test_task.id,
            user_id=test_user.id,
            status="completed",
            run_config={"test": True},
            playground_execution_id="test_exec_456",
            steps_taken=15,
            execution_time_seconds=45.0,
            success_rate=0.9,
            result_data={"score": 95}
        )
        test_db.add(submission)
        test_db.commit()
        test_db.refresh(submission)
        
        response = client.get(
            f"/api/v1/submissions/{submission.id}",
            headers=authenticated_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == submission.id
        assert data["playground_execution_id"] == "test_exec_456"
        assert data["steps_taken"] == 15
        assert data["success_rate"] == 0.9


class TestPlaygroundEndpoints:
    """Test playground execution API endpoints."""

    @pytest.mark.asyncio
    async def test_playground_run_direct(
        self, async_client, authenticated_headers, test_agent, test_task,
        override_playground_service
    ):
        """Test direct playground execution endpoint."""
        run_data = {
            "agent_id": test_agent.id,
            "task_id": test_task.id,
            "agent_config": {
                "model": "claude-3",
                "temperature": 0.5
            },
            "task_config": {
                "url": "http://playground-test.com",
                "goal": "Test playground execution"
            }
        }
        
        response = await async_client.post(
            "/api/v1/playground/run",
            json=run_data,
            headers=authenticated_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] in ["completed", "failed"]
        assert data["execution_id"] is not None
        assert data["steps_taken"] is not None
        assert data["total_time_seconds"] is not None
        assert data["execution_log"] is not None

    def test_playground_run_unauthenticated(self, client):
        """Test playground execution without authentication."""
        run_data = {
            "agent_id": 1,
            "task_id": 1,
            "agent_config": {},
            "task_config": {}
        }
        
        response = client.post("/api/v1/playground/run", json=run_data)
        assert response.status_code == 401


class TestAdminEndpoints:
    """Test admin API endpoints."""

    def test_admin_dashboard_authenticated_admin(
        self, client, admin_headers
    ):
        """Test admin dashboard with admin user."""
        response = client.get("/api/v1/admin/dashboard", headers=admin_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "total_users" in data
        assert "total_agents" in data
        assert "total_tasks" in data
        assert "total_submissions" in data

    def test_admin_dashboard_non_admin(
        self, client, authenticated_headers
    ):
        """Test admin dashboard with regular user."""
        response = client.get("/api/v1/admin/dashboard", headers=authenticated_headers)
        assert response.status_code == 403

    def test_admin_dashboard_unauthenticated(self, client):
        """Test admin dashboard without authentication."""
        response = client.get("/api/v1/admin/dashboard")
        assert response.status_code == 401


class TestDependencyInjection:
    """Test that dependency injection is working correctly."""

    @pytest.mark.asyncio
    async def test_submission_uses_injected_playground_service(
        self, async_client, authenticated_headers, test_agent, test_task,
        override_playground_service
    ):
        """Test that submissions use the injected playground execution service."""
        # The override_playground_service fixture should inject our mock
        submission_data = {
            "agent_id": test_agent.id,
            "task_id": test_task.id,
            "run_config": {"test_injection": True}
        }
        
        response = await async_client.post(
            "/api/v1/submissions",
            json=submission_data,
            headers=authenticated_headers
        )
        assert response.status_code == 201
        
        # Verify that the mock service was used
        data = response.json()
        assert data["playground_execution_id"] is not None
        # The mock service should produce predictable results
        assert isinstance(data["steps_taken"], int)
        assert data["steps_taken"] > 0


class TestErrorHandling:
    """Test API error handling and exception responses."""

    def test_not_found_error_format(self, client, authenticated_headers):
        """Test 404 error response format."""
        response = client.get("/api/v1/agents/99999", headers=authenticated_headers)
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data
        assert "message" in data
        assert "error_code" in data
        assert data["error"] == "Not Found"

    def test_validation_error_format(self, client, authenticated_headers):
        """Test validation error response format."""
        # Send invalid agent data
        invalid_data = {
            "name": "",  # Empty name should fail validation
            "config": "not_a_dict"  # Should be a dict
        }
        
        response = client.post(
            "/api/v1/agents",
            json=invalid_data,
            headers=authenticated_headers
        )
        assert response.status_code == 422  # FastAPI validation error

    def test_unauthorized_error_format(self, client):
        """Test unauthorized error response format."""
        response = client.get("/api/v1/me")
        assert response.status_code == 401
        
        data = response.json()
        assert "detail" in data