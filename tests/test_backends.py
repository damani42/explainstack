"""Tests for ExplainStack backends."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from explainstack.backends import (
    OpenAIBackend,
    ClaudeBackend,
    GeminiBackend,
    BackendFactory
)


class TestOpenAIBackend:
    """Test OpenAI Backend."""
    
    def test_initialization(self):
        """Test backend initialization."""
        config = {
            "api_key": "test-key",
            "model": "gpt-4",
            "temperature": 0.3,
            "max_tokens": 2000
        }
        backend = OpenAIBackend(config)
        assert backend.name == "OpenAI"
        assert backend.config == config
    
    @pytest.mark.asyncio
    @patch('explainstack.backends.openai_backend.openai')
    async def test_generate_response_success(self, mock_openai):
        """Test successful response generation."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_openai.ChatCompletion.acreate = AsyncMock(return_value=mock_response)
        
        config = {"api_key": "test-key", "model": "gpt-4"}
        backend = OpenAIBackend(config)
        
        success, response, error = await backend.generate_response("system", "user")
        
        assert success is True
        assert response == "Test response"
        assert error is None
    
    @pytest.mark.asyncio
    @patch('explainstack.backends.openai_backend.openai')
    async def test_generate_response_error(self, mock_openai):
        """Test error handling in response generation."""
        # Mock OpenAI to raise exception
        mock_openai.ChatCompletion.acreate = AsyncMock(side_effect=Exception("API Error"))
        
        config = {"api_key": "test-key", "model": "gpt-4"}
        backend = OpenAIBackend(config)
        
        success, response, error = await backend.generate_response("system", "user")
        
        assert success is False
        assert response is None
        assert "API Error" in error


class TestClaudeBackend:
    """Test Claude Backend."""
    
    def test_initialization(self):
        """Test backend initialization."""
        config = {
            "api_key": "test-key",
            "model": "claude-3-sonnet-20240229",
            "temperature": 0.2,
            "max_tokens": 3000
        }
        backend = ClaudeBackend(config)
        assert backend.name == "Claude"
        assert backend.config == config
    
    @pytest.mark.asyncio
    @patch('explainstack.backends.claude_backend.anthropic')
    async def test_generate_response_success(self, mock_anthropic):
        """Test successful response generation."""
        # Mock Claude response
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "Test response"
        mock_anthropic.AsyncAnthropic.return_value.messages.create = AsyncMock(return_value=mock_response)
        
        config = {"api_key": "test-key", "model": "claude-3-sonnet-20240229"}
        backend = ClaudeBackend(config)
        
        success, response, error = await backend.generate_response("system", "user")
        
        assert success is True
        assert response == "Test response"
        assert error is None


class TestGeminiBackend:
    """Test Gemini Backend."""
    
    def test_initialization(self):
        """Test backend initialization."""
        config = {
            "api_key": "test-key",
            "model": "gemini-pro",
            "temperature": 0.1,
            "max_tokens": 1000
        }
        backend = GeminiBackend(config)
        assert backend.name == "Gemini"
        assert backend.config == config
    
    @pytest.mark.asyncio
    @patch('explainstack.backends.gemini_backend.genai')
    async def test_generate_response_success(self, mock_genai):
        """Test successful response generation."""
        # Mock Gemini response
        mock_model = Mock()
        mock_model.generate_content_async = AsyncMock(return_value=Mock(text="Test response"))
        mock_genai.configure.return_value = None
        mock_genai.GenerativeModel.return_value = mock_model
        
        config = {"api_key": "test-key", "model": "gemini-pro"}
        backend = GeminiBackend(config)
        
        success, response, error = await backend.generate_response("system", "user")
        
        assert success is True
        assert response == "Test response"
        assert error is None


class TestBackendFactory:
    """Test Backend Factory."""
    
    def test_create_openai_backend(self):
        """Test OpenAI backend creation."""
        config = {"api_key": "test-key", "model": "gpt-4"}
        backend = BackendFactory.create_backend("openai", config)
        assert isinstance(backend, OpenAIBackend)
        assert backend.name == "OpenAI"
    
    def test_create_claude_backend(self):
        """Test Claude backend creation."""
        config = {"api_key": "test-key", "model": "claude-3-sonnet-20240229"}
        backend = BackendFactory.create_backend("claude", config)
        assert isinstance(backend, ClaudeBackend)
        assert backend.name == "Claude"
    
    def test_create_gemini_backend(self):
        """Test Gemini backend creation."""
        config = {"api_key": "test-key", "model": "gemini-pro"}
        backend = BackendFactory.create_backend("gemini", config)
        assert isinstance(backend, GeminiBackend)
        assert backend.name == "Gemini"
    
    def test_create_unknown_backend(self):
        """Test unknown backend creation."""
        with pytest.raises(ValueError, match="Unknown backend type"):
            BackendFactory.create_backend("unknown", {})


class TestBackendIntegration:
    """Test backend integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_backend_configuration_validation(self):
        """Test backend configuration validation."""
        # Test missing API key
        config = {"model": "gpt-4"}
        backend = OpenAIBackend(config)
        assert backend.config["api_key"] == ""
    
    @pytest.mark.asyncio
    async def test_backend_model_override(self):
        """Test backend model override."""
        config = {
            "api_key": "test-key",
            "model": "gpt-3.5-turbo",
            "temperature": 0.5,
            "max_tokens": 1000
        }
        backend = OpenAIBackend(config)
        assert backend.config["model"] == "gpt-3.5-turbo"
        assert backend.config["temperature"] == 0.5
        assert backend.config["max_tokens"] == 1000
