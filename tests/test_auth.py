"""Tests for ExplainStack authentication."""

import pytest
from unittest.mock import Mock, patch
from explainstack.auth import AuthService, AuthMiddleware
from explainstack.database import DatabaseManager
from explainstack.user import UserService, UserPreferencesManager


class TestAuthService:
    """Test Authentication Service."""
    
    @pytest.fixture
    def mock_db_manager(self):
        """Mock database manager."""
        db_manager = Mock(spec=DatabaseManager)
        return db_manager
    
    def test_initialization(self, mock_db_manager):
        """Test auth service initialization."""
        auth_service = AuthService(mock_db_manager)
        assert auth_service.db_manager == mock_db_manager
    
    @pytest.mark.asyncio
    async def test_register_user_success(self, mock_db_manager):
        """Test successful user registration."""
        # Mock database operations
        mock_db_manager.get_session.return_value.__enter__.return_value = Mock()
        mock_db_manager.get_session.return_value.__exit__.return_value = None
        
        auth_service = AuthService(mock_db_manager)
        
        # Mock user creation
        with patch.object(auth_service, '_hash_password', return_value="hashed_password"):
            with patch.object(auth_service, '_create_user', return_value=Mock(id="user-123")):
                result = await auth_service.register_user("test@example.com", "password123")
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_register_user_duplicate_email(self, mock_db_manager):
        """Test registration with duplicate email."""
        # Mock existing user
        mock_db_manager.get_session.return_value.__enter__.return_value = Mock()
        mock_db_manager.get_session.return_value.__exit__.return_value = None
        
        auth_service = AuthService(mock_db_manager)
        
        # Mock user already exists
        with patch.object(auth_service, '_get_user_by_email', return_value=Mock()):
            result = await auth_service.register_user("existing@example.com", "password123")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_login_user_success(self, mock_db_manager):
        """Test successful user login."""
        # Mock user and session
        mock_user = Mock()
        mock_user.id = "user-123"
        mock_user.email = "test@example.com"
        mock_user.password_hash = "hashed_password"
        
        mock_db_manager.get_session.return_value.__enter__.return_value = Mock()
        mock_db_manager.get_session.return_value.__exit__.return_value = None
        
        auth_service = AuthService(mock_db_manager)
        
        # Mock password verification
        with patch.object(auth_service, '_verify_password', return_value=True):
            with patch.object(auth_service, '_get_user_by_email', return_value=mock_user):
                with patch.object(auth_service, '_create_session', return_value="session-123"):
                    result = await auth_service.login_user("test@example.com", "password123")
        
        assert result == "session-123"
    
    @pytest.mark.asyncio
    async def test_login_user_invalid_credentials(self, mock_db_manager):
        """Test login with invalid credentials."""
        mock_db_manager.get_session.return_value.__enter__.return_value = Mock()
        mock_db_manager.get_session.return_value.__exit__.return_value = None
        
        auth_service = AuthService(mock_db_manager)
        
        # Mock user not found
        with patch.object(auth_service, '_get_user_by_email', return_value=None):
            result = await auth_service.login_user("nonexistent@example.com", "password123")
        
        assert result is None
    
    def test_hash_password(self, mock_db_manager):
        """Test password hashing."""
        auth_service = AuthService(mock_db_manager)
        password = "test_password"
        hashed = auth_service._hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
    
    def test_verify_password(self, mock_db_manager):
        """Test password verification."""
        auth_service = AuthService(mock_db_manager)
        password = "test_password"
        hashed = auth_service._hash_password(password)
        
        # Test correct password
        assert auth_service._verify_password(password, hashed) is True
        
        # Test incorrect password
        assert auth_service._verify_password("wrong_password", hashed) is False


class TestAuthMiddleware:
    """Test Authentication Middleware."""
    
    @pytest.fixture
    def mock_auth_service(self):
        """Mock auth service."""
        auth_service = Mock(spec=AuthService)
        return auth_service
    
    def test_initialization(self, mock_auth_service):
        """Test middleware initialization."""
        middleware = AuthMiddleware(mock_auth_service)
        assert middleware.auth_service == mock_auth_service
    
    @pytest.mark.asyncio
    async def test_get_current_user_success(self, mock_auth_service):
        """Test getting current user successfully."""
        mock_user = Mock()
        mock_user.id = "user-123"
        mock_user.email = "test@example.com"
        
        mock_auth_service.get_user_by_session.return_value = mock_user
        
        middleware = AuthMiddleware(mock_auth_service)
        user = middleware.get_current_user("session-123")
        
        assert user == mock_user
        mock_auth_service.get_user_by_session.assert_called_once_with("session-123")
    
    @pytest.mark.asyncio
    async def test_get_current_user_no_session(self, mock_auth_service):
        """Test getting current user with no session."""
        mock_auth_service.get_user_by_session.return_value = None
        
        middleware = AuthMiddleware(mock_auth_service)
        user = middleware.get_current_user("invalid-session")
        
        assert user is None
    
    def test_get_user_config(self, mock_auth_service):
        """Test getting user configuration."""
        mock_user = Mock()
        mock_user.id = "user-123"
        mock_user.preferences = {"theme": "dark", "language": "en"}
        
        middleware = AuthMiddleware(mock_auth_service)
        config = middleware.get_user_config(mock_user)
        
        assert config["user_id"] == "user-123"
        assert config["preferences"] == mock_user.preferences


class TestUserService:
    """Test User Service."""
    
    @pytest.fixture
    def mock_auth_service(self):
        """Mock auth service."""
        return Mock()
    
    def test_initialization(self, mock_auth_service):
        """Test user service initialization."""
        user_service = UserService(mock_auth_service)
        assert user_service.auth_service == mock_auth_service
    
    @pytest.mark.asyncio
    async def test_get_user_profile(self, mock_auth_service):
        """Test getting user profile."""
        mock_user = Mock()
        mock_user.id = "user-123"
        mock_user.email = "test@example.com"
        mock_user.name = "Test User"
        mock_user.created_at = "2024-01-01"
        
        mock_auth_service.get_user_by_id.return_value = mock_user
        
        user_service = UserService(mock_auth_service)
        profile = await user_service.get_user_profile("user-123")
        
        assert profile["id"] == "user-123"
        assert profile["email"] == "test@example.com"
        assert profile["name"] == "Test User"


class TestUserPreferencesManager:
    """Test User Preferences Manager."""
    
    @pytest.fixture
    def mock_auth_service(self):
        """Mock auth service."""
        return Mock()
    
    def test_initialization(self, mock_auth_service):
        """Test preferences manager initialization."""
        preferences_manager = UserPreferencesManager(mock_auth_service)
        assert preferences_manager.auth_service == mock_auth_service
    
    @pytest.mark.asyncio
    async def test_get_user_preferences(self, mock_auth_service):
        """Test getting user preferences."""
        mock_user = Mock()
        mock_user.preferences = {"theme": "dark", "language": "en"}
        
        mock_auth_service.get_user_by_id.return_value = mock_user
        
        preferences_manager = UserPreferencesManager(mock_auth_service)
        preferences = await preferences_manager.get_user_preferences("user-123")
        
        assert preferences == {"theme": "dark", "language": "en"}
    
    @pytest.mark.asyncio
    async def test_update_user_preferences(self, mock_auth_service):
        """Test updating user preferences."""
        mock_user = Mock()
        mock_user.preferences = {}
        
        mock_auth_service.get_user_by_id.return_value = mock_user
        mock_auth_service.update_user.return_value = True
        
        preferences_manager = UserPreferencesManager(mock_auth_service)
        result = await preferences_manager.update_user_preferences(
            "user-123", {"theme": "light", "language": "fr"}
        )
        
        assert result is True
        mock_auth_service.update_user.assert_called_once()
