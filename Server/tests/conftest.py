import os
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.db.database import get_db, Base
from app.core.config import settings
from app.models.user import User
from app.models.agent import Agent
from app.models.task import Task
from app.models.enums import UserRole, TaskDifficulty
from app.services.auth_service import AuthService
from app.services.mock_playground_execution_service import MockPlaygroundExecutionService
from app.api.dependencies import get_current_user, get_playground_execution_service
from main import app

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test_sql_app.db"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def test_db() -> Generator:
    """Create and tear down test database for each test."""
    Base.metadata.create_all(bind=test_engine)
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function") 
def override_get_db(test_db):
    """Override the get_db dependency for testing."""
    def _override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(test_db) -> User:
    """Create a test user."""
    auth_service = AuthService(test_db)
    user = User(
        username="testuser",
        firstName="Test",
        lastName="User",
        email="test@example.com",
        password=auth_service._get_hashed_password("testpassword"),
        role=UserRole.USER,
        isActive=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_admin_user(test_db) -> User:
    """Create a test admin user."""
    auth_service = AuthService(test_db)
    admin = User(
        username="adminuser",
        firstName="Admin",
        lastName="User", 
        email="admin@example.com", 
        password=auth_service._get_hashed_password("adminpassword"),
        role=UserRole.ADMIN,
        isActive=True
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    return admin


@pytest.fixture(scope="function")
def test_agent(test_db, test_user) -> Agent:
    """Create a test agent."""
    agent = Agent(
        name="Test Agent",
        description="A test agent for testing",
        configurationJson={"test": "config"},
        userId=test_user.id
    )
    test_db.add(agent)
    test_db.commit()
    test_db.refresh(agent)
    return agent


@pytest.fixture(scope="function")
def test_task(test_db, test_user) -> Task:
    """Create a test task."""
    task = Task(
        title="Test Task",
        description="A test task for testing",
        difficulty=TaskDifficulty.MEDIUM,
        webArenaEnvironment="test-environment",
        environmentConfig={"test": "config"},
        createdBy=test_user.id
    )
    test_db.add(task)
    test_db.commit()
    test_db.refresh(task)
    return task


@pytest.fixture(scope="function")
def mock_playground_service() -> MockPlaygroundExecutionService:
    """Create a mock playground execution service."""
    return MockPlaygroundExecutionService()


@pytest.fixture(scope="function")
def override_playground_service(mock_playground_service):
    """Override the playground execution service for testing."""
    def _override_playground_service():
        return mock_playground_service
    
    app.dependency_overrides[get_playground_execution_service] = _override_playground_service
    yield mock_playground_service
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_token(test_user, test_db) -> str:
    """Generate a test JWT token."""
    auth_service = AuthService(test_db)
    return auth_service._create_access_token(test_user.id)


@pytest.fixture(scope="function")
def admin_token(test_admin_user, test_db) -> str:
    """Generate an admin JWT token."""
    auth_service = AuthService(test_db)
    return auth_service._create_access_token(test_admin_user.id)


@pytest.fixture(scope="function")
def authenticated_headers(test_token) -> dict:
    """Create headers with authentication token."""
    return {"Authorization": f"Bearer {test_token}"}


@pytest.fixture(scope="function")
def admin_headers(admin_token) -> dict:
    """Create headers with admin authentication token."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="function")
def client(override_get_db) -> TestClient:
    """Create a test client."""
    return TestClient(app)


@pytest.fixture(scope="function")
def async_client(override_get_db) -> AsyncClient:
    """Create an async test client."""
    return AsyncClient(app=app, base_url="http://testserver")