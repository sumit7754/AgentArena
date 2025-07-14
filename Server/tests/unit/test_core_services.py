import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.exceptions import (
    AgentArenaException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
    PlaygroundExecutionException,
    DatabaseException
)
from app.core.pagination import PaginationParams, paginate_query
from app.services.auth_service import AuthService
from app.models.user import User


class TestCoreExceptions:
    """Test custom exception hierarchy."""

    def test_agent_arena_exception_base(self):
        """Test base AgentArenaException."""
        exc = AgentArenaException("Test message", "TEST_CODE")
        assert str(exc) == "Test message"
        assert exc.message == "Test message"
        assert exc.error_code == "TEST_CODE"

    def test_not_found_exception(self):
        """Test NotFoundException."""
        exc = NotFoundException("Resource not found", "NOT_FOUND")
        assert isinstance(exc, AgentArenaException)
        assert exc.message == "Resource not found"
        assert exc.error_code == "NOT_FOUND"

    def test_unauthorized_exception(self):
        """Test UnauthorizedException."""
        exc = UnauthorizedException("Unauthorized access", "UNAUTHORIZED")
        assert isinstance(exc, AgentArenaException)
        assert exc.message == "Unauthorized access"

    def test_validation_exception(self):
        """Test ValidationException."""
        exc = ValidationException("Invalid input", "VALIDATION_ERROR")
        assert isinstance(exc, AgentArenaException)
        assert exc.message == "Invalid input"

    def test_playground_execution_exception(self):
        """Test PlaygroundExecutionException."""
        exc = PlaygroundExecutionException("Execution failed", "EXECUTION_ERROR")
        assert isinstance(exc, AgentArenaException)
        assert exc.message == "Execution failed"

    def test_database_exception(self):
        """Test DatabaseException."""
        exc = DatabaseException("Database error", "DB_ERROR")
        assert isinstance(exc, AgentArenaException)
        assert exc.message == "Database error"


class TestPagination:
    """Test pagination utilities."""

    def test_pagination_params_defaults(self):
        """Test default pagination parameters."""
        params = PaginationParams()
        assert params.page == 1
        assert params.size == 10
        assert params.size <= 100  # Max size limit

    def test_pagination_params_custom(self):
        """Test custom pagination parameters."""
        params = PaginationParams(page=3, size=25)
        assert params.page == 3
        assert params.size == 25

    def test_pagination_params_validation(self):
        """Test pagination parameter validation."""
        # Test minimum page
        with pytest.raises(ValueError):
            PaginationParams(page=0)
        
        # Test minimum size
        with pytest.raises(ValueError):
            PaginationParams(size=0)
        
        # Test maximum size
        with pytest.raises(ValueError):
            PaginationParams(size=101)

    def test_pagination_offset_calculation(self):
        """Test offset calculation for pagination."""
        params = PaginationParams(page=1, size=10)
        assert params.offset == 0
        
        params = PaginationParams(page=2, size=10)
        assert params.offset == 10
        
        params = PaginationParams(page=3, size=20)
        assert params.offset == 40

    def test_paginate_query_mock(self):
        """Test paginate_query function with mock data."""
        # Mock query object
        mock_query = Mock()
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [1, 2, 3, 4, 5]
        mock_query.count.return_value = 15
        
        params = PaginationParams(page=2, size=5)
        result = paginate_query(mock_query, params)
        
        assert result.items == [1, 2, 3, 4, 5]
        assert result.total == 15
        assert result.page == 2
        assert result.size == 5
        assert result.pages == 3
        assert result.has_next == True
        assert result.has_prev == True


class TestAuthService:
    """Test authentication service."""

    def test_password_hashing(self):
        """Test password hashing and verification."""
        auth_service = AuthService()
        password = "test_password_123"
        
        # Hash password
        hashed = auth_service.get_password_hash(password)
        assert hashed != password
        assert len(hashed) > 0
        
        # Verify correct password
        assert auth_service.verify_password(password, hashed) == True
        
        # Verify incorrect password
        assert auth_service.verify_password("wrong_password", hashed) == False

    def test_jwt_token_creation(self):
        """Test JWT token creation."""
        auth_service = AuthService()
        data = {"sub": "123", "username": "testuser"}
        
        token = auth_service.create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 0
        assert "." in token  # JWT has dots

    def test_jwt_token_creation_with_expiry(self):
        """Test JWT token creation with custom expiry."""
        auth_service = AuthService()
        data = {"sub": "123"}
        expires_delta = timedelta(minutes=15)
        
        token = auth_service.create_access_token(data, expires_delta)
        assert isinstance(token, str)
        assert len(token) > 0

    @patch('app.services.auth_service.jwt.decode')
    def test_jwt_token_verification_success(self, mock_decode):
        """Test successful JWT token verification."""
        auth_service = AuthService()
        mock_decode.return_value = {"sub": "123", "exp": datetime.now().timestamp() + 3600}
        
        payload = auth_service.verify_token("valid_token")
        assert payload["sub"] == "123"

    @patch('app.services.auth_service.jwt.decode')
    def test_jwt_token_verification_failure(self, mock_decode):
        """Test JWT token verification failure."""
        auth_service = AuthService()
        from jose import JWTError
        mock_decode.side_effect = JWTError("Invalid token")
        
        with pytest.raises(UnauthorizedException):
            auth_service.verify_token("invalid_token")

    def test_authenticate_user_success(self, test_db):
        """Test successful user authentication."""
        auth_service = AuthService()
        
        # Create a test user
        hashed_password = auth_service.get_password_hash("testpass")
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=hashed_password,
            is_active=True
        )
        test_db.add(user)
        test_db.commit()
        
        # Authenticate
        authenticated_user = auth_service.authenticate_user(
            test_db, "testuser", "testpass"
        )
        
        assert authenticated_user is not None
        assert authenticated_user.username == "testuser"

    def test_authenticate_user_wrong_password(self, test_db):
        """Test authentication with wrong password."""
        auth_service = AuthService()
        
        # Create a test user
        hashed_password = auth_service.get_password_hash("testpass")
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=hashed_password,
            is_active=True
        )
        test_db.add(user)
        test_db.commit()
        
        # Authenticate with wrong password
        result = auth_service.authenticate_user(
            test_db, "testuser", "wrongpass"
        )
        
        assert result is None

    def test_authenticate_user_not_found(self, test_db):
        """Test authentication with non-existent user."""
        auth_service = AuthService()
        
        result = auth_service.authenticate_user(
            test_db, "nonexistent", "password"
        )
        
        assert result is None

    def test_authenticate_inactive_user(self, test_db):
        """Test authentication with inactive user."""
        auth_service = AuthService()
        
        # Create an inactive test user
        hashed_password = auth_service.get_password_hash("testpass")
        user = User(
            username="inactiveuser",
            email="inactive@example.com",
            hashed_password=hashed_password,
            is_active=False
        )
        test_db.add(user)
        test_db.commit()
        
        # Try to authenticate
        result = auth_service.authenticate_user(
            test_db, "inactiveuser", "testpass"
        )
        
        assert result is None  # Should reject inactive users

    def test_get_user_by_id(self, test_db):
        """Test getting user by ID."""
        auth_service = AuthService()
        
        # Create a test user
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed",
            is_active=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Get user by ID
        found_user = auth_service.get_user_by_id(test_db, user.id)
        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.username == "testuser"
        
        # Test with non-existent ID
        not_found = auth_service.get_user_by_id(test_db, 99999)
        assert not_found is None

    def test_get_user_by_username(self, test_db):
        """Test getting user by username."""
        auth_service = AuthService()
        
        # Create a test user
        user = User(
            username="uniqueuser",
            email="unique@example.com",
            hashed_password="hashed",
            is_active=True
        )
        test_db.add(user)
        test_db.commit()
        
        # Get user by username
        found_user = auth_service.get_user_by_username(test_db, "uniqueuser")
        assert found_user is not None
        assert found_user.username == "uniqueuser"
        
        # Test with non-existent username
        not_found = auth_service.get_user_by_username(test_db, "nonexistent")
        assert not_found is None