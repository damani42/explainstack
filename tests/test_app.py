"""Tests for ExplainStack main application."""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import os
import tempfile
from explainstack.app import (
    setup_openai,
    validate_input,
    handle_file_upload,
    handle_gerrit_url,
    handle_analytics
)


class TestSetupOpenAI:
    """Test OpenAI setup function."""
    
    def test_setup_openai_success(self):
        """Test successful OpenAI setup."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            with patch('explainstack.app.openai') as mock_openai:
                result = setup_openai()
                assert result is True
                mock_openai.api_key = 'test-key'
    
    def test_setup_openai_missing_key(self):
        """Test OpenAI setup with missing API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(RuntimeError, match="Configuration error"):
                setup_openai()
    
    def test_setup_openai_load_dotenv(self):
        """Test OpenAI setup with dotenv loading."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('explainstack.app.load_dotenv') as mock_load_dotenv:
                with patch('explainstack.app.os.getenv', return_value='test-key'):
                    with patch('explainstack.app.openai'):
                        result = setup_openai()
                        assert result is True
                        mock_load_dotenv.assert_called_once()


class TestValidateInput:
    """Test input validation function."""
    
    def test_validate_input_success(self):
        """Test successful input validation."""
        result = validate_input("This is a valid input")
        assert result == (True, None)
    
    def test_validate_input_empty(self):
        """Test validation with empty input."""
        result = validate_input("")
        assert result == (False, "Message cannot be empty")
    
    def test_validate_input_whitespace(self):
        """Test validation with whitespace only."""
        result = validate_input("   ")
        assert result == (False, "Message cannot be empty")
    
    def test_validate_input_too_long(self):
        """Test validation with input too long."""
        long_input = "x" * 15000  # Exceeds max length
        result = validate_input(long_input)
        assert result == (False, "Message too long")
    
    def test_validate_input_too_short(self):
        """Test validation with input too short."""
        result = validate_input("")
        assert result == (False, "Message cannot be empty")


class TestHandleFileUpload:
    """Test file upload handling."""
    
    @pytest.mark.asyncio
    async def test_handle_file_upload_success(self):
        """Test successful file upload."""
        # Mock file element
        mock_element = Mock()
        mock_element.content = b"print('hello world')"
        mock_element.name = "test.py"
        
        # Mock file handler
        with patch('explainstack.app.file_handler') as mock_handler:
            mock_handler.save_uploaded_file.return_value = (True, "/tmp/test.py", None)
            mock_handler.process_file_for_analysis.return_value = (
                True, 
                {
                    'filename': 'test.py',
                    'content': "print('hello world')",
                    'size': 20,
                    'lines': 1,
                    'extension': '.py'
                }, 
                None
            )
            
            # Mock Chainlit
            with patch('explainstack.app.cl.Message') as mock_message:
                await handle_file_upload([mock_element])
                
                # Verify file handler calls
                mock_handler.save_uploaded_file.assert_called_once()
                mock_handler.process_file_for_analysis.assert_called_once()
                
                # Verify message sent
                mock_message.assert_called()
    
    @pytest.mark.asyncio
    async def test_handle_file_upload_error(self):
        """Test file upload with error."""
        # Mock file element
        mock_element = Mock()
        mock_element.content = b"print('hello world')"
        mock_element.name = "test.py"
        
        # Mock file handler to return error
        with patch('explainstack.app.file_handler') as mock_handler:
            mock_handler.save_uploaded_file.return_value = (False, None, "File too large")
            
            # Mock Chainlit
            with patch('explainstack.app.cl.Message') as mock_message:
                await handle_file_upload([mock_element])
                
                # Verify error message sent
                mock_message.assert_called()
                call_args = mock_message.call_args[0][0]
                assert "Error uploading file" in call_args
    
    @pytest.mark.asyncio
    async def test_handle_file_upload_exception(self):
        """Test file upload with exception."""
        # Mock file element
        mock_element = Mock()
        mock_element.content = b"print('hello world')"
        mock_element.name = "test.py"
        
        # Mock file handler to raise exception
        with patch('explainstack.app.file_handler') as mock_handler:
            mock_handler.save_uploaded_file.side_effect = Exception("Unexpected error")
            
            # Mock Chainlit
            with patch('explainstack.app.cl.Message') as mock_message:
                await handle_file_upload([mock_element])
                
                # Verify error message sent
                mock_message.assert_called()
                call_args = mock_message.call_args[0][0]
                assert "Error processing uploaded file" in call_args


class TestHandleGerritUrl:
    """Test Gerrit URL handling."""
    
    @pytest.mark.asyncio
    async def test_handle_gerrit_url_success(self):
        """Test successful Gerrit URL analysis."""
        test_url = "https://review.opendev.org/c/openstack/nova/+/12345"
        
        # Mock Gerrit integration
        with patch('explainstack.app.gerrit_integration') as mock_gerrit:
            mock_gerrit.analyze_gerrit_url.return_value = (
                True,
                {
                    'summary': {'subject': 'Test change'},
                    'diff_content': 'diff content'
                },
                None
            )
            mock_gerrit.format_gerrit_analysis.return_value = "Formatted analysis"
            
            # Mock Chainlit
            with patch('explainstack.app.cl.Message') as mock_message:
                with patch('explainstack.app.cl.user_session') as mock_session:
                    await handle_gerrit_url(test_url)
                    
                    # Verify Gerrit analysis called
                    mock_gerrit.analyze_gerrit_url.assert_called_once_with(test_url)
                    mock_gerrit.format_gerrit_analysis.assert_called_once()
                    
                    # Verify messages sent
                    assert mock_message.call_count >= 2  # Loading + result
                    
                    # Verify session data stored
                    mock_session.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_gerrit_url_error(self):
        """Test Gerrit URL analysis with error."""
        test_url = "https://review.opendev.org/c/openstack/nova/+/12345"
        
        # Mock Gerrit integration to return error
        with patch('explainstack.app.gerrit_integration') as mock_gerrit:
            mock_gerrit.analyze_gerrit_url.return_value = (
                False, None, "Failed to fetch change"
            )
            
            # Mock Chainlit
            with patch('explainstack.app.cl.Message') as mock_message:
                await handle_gerrit_url(test_url)
                
                # Verify error message sent
                mock_message.assert_called()
                call_args = mock_message.call_args[0][0]
                assert "Error analyzing Gerrit URL" in call_args
    
    @pytest.mark.asyncio
    async def test_handle_gerrit_url_exception(self):
        """Test Gerrit URL analysis with exception."""
        test_url = "https://review.opendev.org/c/openstack/nova/+/12345"
        
        # Mock Gerrit integration to raise exception
        with patch('explainstack.app.gerrit_integration') as mock_gerrit:
            mock_gerrit.analyze_gerrit_url.side_effect = Exception("Network error")
            
            # Mock Chainlit
            with patch('explainstack.app.cl.Message') as mock_message:
                await handle_gerrit_url(test_url)
                
                # Verify error message sent
                mock_message.assert_called()
                call_args = mock_message.call_args[0][0]
                assert "Error analyzing Gerrit URL" in call_args


class TestHandleAnalytics:
    """Test analytics dashboard handling."""
    
    @pytest.mark.asyncio
    async def test_handle_analytics_success(self):
        """Test successful analytics display."""
        # Mock user and session
        mock_user = Mock()
        mock_user.id = "user-123"
        
        # Mock auth middleware
        with patch('explainstack.app.auth_middleware') as mock_auth:
            mock_auth.get_current_user.return_value = mock_user
            
            # Mock analytics manager
            with patch('explainstack.app.analytics_manager') as mock_analytics:
                mock_analytics.get_dashboard_data.return_value = {"metrics": "data"}
                mock_analytics.generate_analytics_report.return_value = "Analytics report"
                
                # Mock Chainlit
                with patch('explainstack.app.cl.user_session') as mock_session:
                    mock_session.get.return_value = "session-123"
                    
                    with patch('explainstack.app.cl.Message') as mock_message:
                        await handle_analytics()
                        
                        # Verify analytics calls
                        mock_analytics.get_dashboard_data.assert_called_once()
                        mock_analytics.generate_analytics_report.assert_called_once()
                        
                        # Verify message sent
                        mock_message.assert_called()
    
    @pytest.mark.asyncio
    async def test_handle_analytics_no_user(self):
        """Test analytics with no authenticated user."""
        # Mock auth middleware to return no user
        with patch('explainstack.app.auth_middleware') as mock_auth:
            mock_auth.get_current_user.return_value = None
            
            # Mock Chainlit
            with patch('explainstack.app.cl.user_session') as mock_session:
                mock_session.get.return_value = "session-123"
                
                with patch('explainstack.app.cl.Message') as mock_message:
                    await handle_analytics()
                    
                    # Verify login required message
                    mock_message.assert_called()
                    call_args = mock_message.call_args[0][0]
                    assert "Please log in to view analytics" in call_args
    
    @pytest.mark.asyncio
    async def test_handle_analytics_exception(self):
        """Test analytics with exception."""
        # Mock user
        mock_user = Mock()
        mock_user.id = "user-123"
        
        # Mock auth middleware
        with patch('explainstack.app.auth_middleware') as mock_auth:
            mock_auth.get_current_user.return_value = mock_user
            
            # Mock analytics manager to raise exception
            with patch('explainstack.app.analytics_manager') as mock_analytics:
                mock_analytics.get_dashboard_data.side_effect = Exception("Database error")
                
                # Mock Chainlit
                with patch('explainstack.app.cl.user_session') as mock_session:
                    mock_session.get.return_value = "session-123"
                    
                    with patch('explainstack.app.cl.Message') as mock_message:
                        await handle_analytics()
                        
                        # Verify error message sent
                        mock_message.assert_called()
                        call_args = mock_message.call_args[0][0]
                        assert "Error loading analytics" in call_args


class TestAppIntegration:
    """Test application integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_main_function_file_upload(self):
        """Test main function with file upload."""
        # Mock message with elements
        mock_message = Mock()
        mock_message.elements = [Mock()]
        mock_message.content = "test"
        
        # Mock file upload handler
        with patch('explainstack.app.handle_file_upload') as mock_upload:
            mock_upload.return_value = None
            
            # Import and call main function
            from explainstack.app import main
            await main(mock_message)
            
            # Verify file upload handler called
            mock_upload.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_main_function_gerrit_url(self):
        """Test main function with Gerrit URL."""
        # Mock message with Gerrit URL
        mock_message = Mock()
        mock_message.elements = None
        mock_message.content = "https://review.opendev.org/c/openstack/nova/+/12345"
        
        # Mock Gerrit integration
        with patch('explainstack.app.gerrit_integration') as mock_gerrit:
            mock_gerrit.is_gerrit_url.return_value = True
            
            with patch('explainstack.app.handle_gerrit_url') as mock_handle:
                # Import and call main function
                from explainstack.app import main
                await main(mock_message)
                
                # Verify Gerrit handler called
                mock_handle.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_main_function_analytics_command(self):
        """Test main function with analytics command."""
        # Mock message with analytics command
        mock_message = Mock()
        mock_message.elements = None
        mock_message.content = "analytics"
        
        # Mock analytics handler
        with patch('explainstack.app.handle_analytics') as mock_analytics:
            # Import and call main function
            from explainstack.app import main
            await main(mock_message)
            
            # Verify analytics handler called
            mock_analytics.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_main_function_exception_handling(self):
        """Test main function exception handling."""
        # Mock message that will cause exception
        mock_message = Mock()
        mock_message.elements = None
        mock_message.content = "test"
        mock_message.side_effect = Exception("Test exception")
        
        # Mock Chainlit
        with patch('explainstack.app.cl.Message') as mock_message_class:
            # Import and call main function
            from explainstack.app import main
            await main(mock_message)
            
            # Verify error message sent
            mock_message_class.assert_called()
            call_args = mock_message_class.call_args[0][0]
            assert "unexpected error occurred" in call_args.lower()


class TestAppConfiguration:
    """Test application configuration."""
    
    def test_config_loading(self):
        """Test configuration loading."""
        from explainstack.app import config
        assert isinstance(config, dict)
        assert "backends" in config
        assert "validation" in config
        assert "logging" in config
    
    def test_logging_configuration(self):
        """Test logging configuration."""
        from explainstack.app import logger
        assert logger.name == "explainstack.app"
    
    def test_services_initialization(self):
        """Test services initialization."""
        from explainstack.app import (
            db_manager,
            auth_service,
            agent_config,
            agent_router,
            file_handler,
            gerrit_integration,
            analytics_manager
        )
        
        # Verify all services are initialized
        assert db_manager is not None
        assert auth_service is not None
        assert agent_config is not None
        assert agent_router is not None
        assert file_handler is not None
        assert gerrit_integration is not None
        assert analytics_manager is not None
