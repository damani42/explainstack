"""Integration tests for ExplainStack."""

import pytest
import asyncio
from unittest.mock import Mock, patch
import tempfile
import os

from explainstack.app import main
from explainstack.agents import CodeExpertAgent, SecurityExpertAgent, PerformanceExpertAgent
from explainstack.backends import OpenAIBackend, ClaudeBackend, GeminiBackend
from explainstack.database import DatabaseManager
from explainstack.auth import AuthService, AuthMiddleware
from explainstack.user import UserService, UserPreferencesManager
from explainstack.utils import FileHandler
from explainstack.integrations import GerritIntegration
from explainstack.analytics import AnalyticsManager


class TestIntegration:
    """Integration tests for ExplainStack components."""
    
    @pytest.mark.integration
    def test_full_agent_workflow(self):
        """Test complete agent workflow from input to response."""
        # Mock backend
        mock_backend = Mock()
        mock_backend.generate_response.return_value = ("Test response", 100, 0.01)
        
        # Test all agents
        agents = [
            CodeExpertAgent(mock_backend),
            SecurityExpertAgent(mock_backend),
            PerformanceExpertAgent(mock_backend)
        ]
        
        for agent in agents:
            success, result, error = asyncio.run(agent.process("test input"))
            assert success is True
            assert result is not None
            assert error is None
    
    @pytest.mark.integration
    def test_database_integration(self):
        """Test database operations integration."""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_manager = DatabaseManager(db_path)
            
            # Test user creation and retrieval
            user_id = db_manager.create_user("test@example.com", "password123")
            assert user_id is not None
            
            user = db_manager.get_user("test@example.com")
            assert user is not None
            assert user.email == "test@example.com"
            
            # Test user preferences
            preferences_manager = UserPreferencesManager(db_manager)
            preferences_manager.set_preference(user_id, "default_agent", "code_expert")
            
            preference = preferences_manager.get_preference(user_id, "default_agent")
            assert preference == "code_expert"
            
        finally:
            # Clean up
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    @pytest.mark.integration
    def test_authentication_flow(self):
        """Test complete authentication flow."""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_manager = DatabaseManager(db_path)
            auth_service = AuthService(db_manager)
            auth_middleware = AuthMiddleware(auth_service)
            
            # Test user registration
            user_id = auth_service.register_user("test@example.com", "password123")
            assert user_id is not None
            
            # Test user login
            session_id = auth_service.login_user("test@example.com", "password123")
            assert session_id is not None
            
            # Test session validation
            current_user = auth_middleware.get_current_user(session_id)
            assert current_user is not None
            assert current_user.email == "test@example.com"
            
            # Test logout
            auth_service.logout_user(session_id)
            current_user = auth_middleware.get_current_user(session_id)
            assert current_user is None
            
        finally:
            # Clean up
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    @pytest.mark.integration
    def test_file_processing_integration(self):
        """Test file processing with different file types."""
        file_handler = FileHandler()
        
        # Test Python file
        python_content = """
def hello_world():
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
"""
        success, result, error = file_handler.process_file_for_analysis(
            "test.py", python_content
        )
        assert success is True
        assert result is not None
        assert result['extension'] == '.py'
        assert result['lines'] > 0
        
        # Test diff file
        diff_content = """
--- a/test.py
+++ b/test.py
@@ -1,3 +1,3 @@
 def hello_world():
-    print("Hello, World!")
+    print("Hello, Universe!")
"""
        success, result, error = file_handler.process_file_for_analysis(
            "test.diff", diff_content
        )
        assert success is True
        assert result is not None
        assert result['extension'] == '.diff'
    
    @pytest.mark.integration
    def test_gerrit_integration(self):
        """Test Gerrit integration functionality."""
        gerrit_integration = GerritIntegration()
        
        # Test URL validation
        valid_url = "https://review.opendev.org/c/openstack/nova/+/12345"
        assert gerrit_integration.is_gerrit_url(valid_url) is True
        
        invalid_url = "https://github.com/user/repo"
        assert gerrit_integration.is_gerrit_url(invalid_url) is False
        
        # Test URL parsing
        parsed = gerrit_integration._parse_gerrit_url(valid_url)
        assert parsed is not None
        project, change_id, revision_id = parsed
        assert project == "openstack/nova"
        assert change_id == "12345"
        assert revision_id is None
    
    @pytest.mark.integration
    def test_analytics_integration(self):
        """Test analytics data collection and reporting."""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_manager = DatabaseManager(db_path)
            analytics_manager = AnalyticsManager()
            
            # Test tracking agent usage
            analytics_manager.track_agent_usage(
                agent_id="test_agent",
                user_id="user123",
                tokens_used=100,
                cost=0.01,
                response_time=0.5,
                success=True
            )
            
            # Test dashboard data
            dashboard_data = analytics_manager.get_dashboard_data("user123", hours=24)
            assert dashboard_data is not None
            
            # Test analytics report
            report = analytics_manager.generate_analytics_report(hours=24)
            assert report is not None
            assert "Analytics Dashboard" in report
            
        finally:
            # Clean up
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    @pytest.mark.integration
    def test_multi_backend_integration(self):
        """Test integration with multiple AI backends."""
        backends = [
            OpenAIBackend({"api_key": "test", "model": "gpt-4"}),
            ClaudeBackend({"api_key": "test", "model": "claude-3-sonnet"}),
            GeminiBackend({"api_key": "test", "model": "gemini-pro"})
        ]
        
        for backend in backends:
            # Mock API calls
            with patch.object(backend, '_make_api_call') as mock_call:
                mock_call.return_value = ("Test response", 100, 0.01)
                
                success, result, error = asyncio.run(
                    backend.generate_response("test prompt", "test system prompt")
                )
                assert success is True
                assert result is not None
                assert error is None
    
    @pytest.mark.integration
    def test_cli_integration(self):
        """Test CLI integration with agents."""
        from explainstack.cli.main import main as cli_main
        from explainstack.cli.commands import AnalyzeCommand
        
        # Mock agent router
        with patch('explainstack.cli.main.agent_router') as mock_router:
            mock_agent = Mock()
            mock_agent.process.return_value = ("Test response", 100, 0.01)
            mock_router.get_agent.return_value = mock_agent
            
            # Test analyze command
            command = AnalyzeCommand(mock_router)
            result = command.execute(Mock(file="test.py"))
            assert "Test response" in result
    
    @pytest.mark.integration
    def test_error_handling_integration(self):
        """Test error handling across the entire system."""
        # Test backend error handling
        mock_backend = Mock()
        mock_backend.generate_response.side_effect = Exception("API Error")
        
        agent = CodeExpertAgent(mock_backend)
        success, result, error = asyncio.run(agent.process("test input"))
        
        assert success is False
        assert result is None
        assert error is not None
        
        # Test database error handling
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_manager = DatabaseManager(db_path)
            
            # Test with invalid data
            user_id = db_manager.create_user("invalid-email", "short")
            assert user_id is None
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    @pytest.mark.integration
    def test_concurrent_operations(self):
        """Test concurrent operations across the system."""
        # Test concurrent agent processing
        mock_backend = Mock()
        mock_backend.generate_response.return_value = ("Test response", 100, 0.01)
        
        agent = CodeExpertAgent(mock_backend)
        
        async def process_request(request_id):
            return await agent.process(f"test input {request_id}")
        
        # Run multiple concurrent requests
        tasks = [process_request(i) for i in range(5)]
        results = asyncio.run(asyncio.gather(*tasks))
        
        # All requests should complete successfully
        for success, result, error in results:
            assert success is True
            assert result is not None
            assert error is None
    
    @pytest.mark.integration
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow."""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # Initialize all services
            db_manager = DatabaseManager(db_path)
            auth_service = AuthService(db_manager)
            auth_middleware = AuthMiddleware(auth_service)
            user_service = UserService(db_manager)
            preferences_manager = UserPreferencesManager(db_manager)
            
            # Create user
            user_id = auth_service.register_user("test@example.com", "password123")
            assert user_id is not None
            
            # Login user
            session_id = auth_service.login_user("test@example.com", "password123")
            assert session_id is not None
            
            # Set user preferences
            preferences_manager.set_preference(user_id, "default_agent", "code_expert")
            
            # Test agent processing
            mock_backend = Mock()
            mock_backend.generate_response.return_value = ("Test response", 100, 0.01)
            
            agent = CodeExpertAgent(mock_backend)
            success, result, error = asyncio.run(agent.process("test input"))
            
            assert success is True
            assert result is not None
            assert error is None
            
        finally:
            # Clean up
            if os.path.exists(db_path):
                os.unlink(db_path)
