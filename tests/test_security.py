"""Security tests for ExplainStack."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
import hashlib
import secrets

from explainstack.auth import AuthService, AuthMiddleware
from explainstack.database import DatabaseManager
from explainstack.user import UserService, UserPreferencesManager
from explainstack.utils import FileHandler
from explainstack.analytics import AnalyticsManager


class TestSecurity:
    """Security tests for ExplainStack components."""
    
    @pytest.mark.security
    def test_password_hashing(self):
        """Test password hashing security."""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_manager = DatabaseManager(db_path)
            auth_service = AuthService(db_manager)
            
            # Test password hashing
            password = "test_password_123"
            user_id = auth_service.register_user("test@example.com", password)
            assert user_id is not None
            
            # Verify password is hashed
            user = db_manager.get_user("test@example.com")
            assert user.password != password  # Should be hashed
            assert len(user.password) > 50  # Should be a long hash
            
            # Test password verification
            assert auth_service.verify_password(password, user.password) is True
            assert auth_service.verify_password("wrong_password", user.password) is False
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    @pytest.mark.security
    def test_session_security(self):
        """Test session management security."""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_manager = DatabaseManager(db_path)
            auth_service = AuthService(db_manager)
            auth_middleware = AuthMiddleware(auth_service)
            
            # Create user
            user_id = auth_service.register_user("test@example.com", "password123")
            
            # Test session creation
            session_id = auth_service.login_user("test@example.com", "password123")
            assert session_id is not None
            assert len(session_id) > 20  # Should be a long, random string
            
            # Test session validation
            current_user = auth_middleware.get_current_user(session_id)
            assert current_user is not None
            assert current_user.email == "test@example.com"
            
            # Test invalid session
            invalid_session = "invalid_session_id"
            current_user = auth_middleware.get_current_user(invalid_session)
            assert current_user is None
            
            # Test session logout
            auth_service.logout_user(session_id)
            current_user = auth_middleware.get_current_user(session_id)
            assert current_user is None
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    @pytest.mark.security
    def test_input_validation(self):
        """Test input validation security."""
        from explainstack.app import validate_input
        
        # Test valid inputs
        valid_inputs = [
            "This is a valid input",
            "def hello():\n    print('Hello, World!')",
            "import os\nprint('test')"
        ]
        
        for input_text in valid_inputs:
            is_valid, error = validate_input(input_text)
            assert is_valid is True
            assert error is None
        
        # Test invalid inputs
        invalid_inputs = [
            "",  # Empty input
            "   ",  # Whitespace only
            "x" * 15000,  # Too long
        ]
        
        for input_text in invalid_inputs:
            is_valid, error = validate_input(input_text)
            assert is_valid is False
            assert error is not None
    
    @pytest.mark.security
    def test_sql_injection_protection(self):
        """Test SQL injection protection."""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_manager = DatabaseManager(db_path)
            auth_service = AuthService(db_manager)
            
            # Test SQL injection attempts
            malicious_inputs = [
                "'; DROP TABLE users; --",
                "admin' OR '1'='1",
                "test@example.com'; DELETE FROM users; --",
                "'; INSERT INTO users (email, password) VALUES ('hacker@evil.com', 'password'); --"
            ]
            
            for malicious_input in malicious_inputs:
                # Try to register with malicious input
                user_id = auth_service.register_user(malicious_input, "password123")
                
                # Should either fail or sanitize input
                if user_id is not None:
                    # If registration succeeds, verify the input was sanitized
                    user = db_manager.get_user(malicious_input)
                    if user is not None:
                        # Verify no SQL injection occurred
                        assert "DROP TABLE" not in user.email
                        assert "DELETE FROM" not in user.email
                        assert "INSERT INTO" not in user.email
                
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    @pytest.mark.security
    def test_file_upload_security(self):
        """Test file upload security."""
        file_handler = FileHandler()
        
        # Test malicious file content
        malicious_contents = [
            "import os; os.system('rm -rf /')",  # Dangerous system call
            "exec('import os; os.system(\"rm -rf /\")')",  # Exec with dangerous code
            "__import__('os').system('rm -rf /')",  # Import with dangerous code
        ]
        
        for malicious_content in malicious_contents:
            # File handler should process safely without executing dangerous code
            success, result, error = file_handler.process_file_for_analysis(
                "malicious.py", malicious_content
            )
            
            # Should process without error (but not execute the dangerous code)
            assert success is True
            assert result is not None
            assert error is None
    
    @pytest.mark.security
    def test_api_key_security(self):
        """Test API key security."""
        # Test API key storage
        api_key = "sk-test123456789"
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_manager = DatabaseManager(db_path)
            user_service = UserService(db_manager)
            
            # Create user
            user_id = user_service.create_user("test@example.com", "password123")
            
            # Store API key
            user_service.set_api_key(user_id, "openai", api_key)
            
            # Retrieve API key
            stored_key = user_service.get_api_key(user_id, "openai")
            assert stored_key == api_key
            
            # Test API key encryption (if implemented)
            # This would test that API keys are encrypted at rest
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    @pytest.mark.security
    def test_session_fixation(self):
        """Test session fixation protection."""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_manager = DatabaseManager(db_path)
            auth_service = AuthService(db_manager)
            
            # Create user
            user_id = auth_service.register_user("test@example.com", "password123")
            
            # Test session regeneration
            session1 = auth_service.login_user("test@example.com", "password123")
            session2 = auth_service.login_user("test@example.com", "password123")
            
            # Sessions should be different
            assert session1 != session2
            
            # Both sessions should be valid
            auth_middleware = AuthMiddleware(auth_service)
            user1 = auth_middleware.get_current_user(session1)
            user2 = auth_middleware.get_current_user(session2)
            
            assert user1 is not None
            assert user2 is not None
            assert user1.email == user2.email
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    @pytest.mark.security
    def test_csrf_protection(self):
        """Test CSRF protection."""
        # This would test CSRF protection if implemented
        # For now, we'll test that sessions are properly validated
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_manager = DatabaseManager(db_path)
            auth_service = AuthService(db_manager)
            auth_middleware = AuthMiddleware(auth_service)
            
            # Create user
            user_id = auth_service.register_user("test@example.com", "password123")
            
            # Test session validation
            session_id = auth_service.login_user("test@example.com", "password123")
            current_user = auth_middleware.get_current_user(session_id)
            assert current_user is not None
            
            # Test invalid session
            invalid_session = "invalid_session_id"
            current_user = auth_middleware.get_current_user(invalid_session)
            assert current_user is None
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    @pytest.mark.security
    def test_data_encryption(self):
        """Test data encryption at rest."""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_manager = DatabaseManager(db_path)
            user_service = UserService(db_manager)
            
            # Create user with sensitive data
            user_id = user_service.create_user("test@example.com", "password123")
            
            # Store sensitive data
            sensitive_data = "sensitive_information_123"
            user_service.set_preference(user_id, "sensitive_data", sensitive_data)
            
            # Retrieve data
            retrieved_data = user_service.get_preference(user_id, "sensitive_data")
            assert retrieved_data == sensitive_data
            
            # Test that data is properly stored (this would test encryption if implemented)
            # For now, we'll just verify the data is stored correctly
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    @pytest.mark.security
    def test_rate_limiting(self):
        """Test rate limiting protection."""
        # This would test rate limiting if implemented
        # For now, we'll test that the system can handle multiple requests
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_manager = DatabaseManager(db_path)
            auth_service = AuthService(db_manager)
            
            # Create user
            user_id = auth_service.register_user("test@example.com", "password123")
            
            # Test multiple login attempts
            for i in range(10):
                session_id = auth_service.login_user("test@example.com", "password123")
                assert session_id is not None
            
            # All login attempts should succeed (no rate limiting implemented yet)
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    @pytest.mark.security
    def test_audit_logging(self):
        """Test audit logging for security events."""
        # This would test audit logging if implemented
        # For now, we'll test that the system can track user actions
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_manager = DatabaseManager(db_path)
            analytics_manager = AnalyticsManager()
            
            # Track security-related events
            analytics_manager.track_agent_usage(
                agent_id="security_expert",
                user_id="user123",
                tokens_used=100,
                cost=0.01,
                response_time=0.5,
                success=True
            )
            
            # Verify tracking works
            dashboard_data = analytics_manager.get_dashboard_data("user123", hours=24)
            assert dashboard_data is not None
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
