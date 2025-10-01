"""Tests for ExplainStack agents."""

import pytest
from unittest.mock import Mock, AsyncMock
from explainstack.agents import (
    CodeExpertAgent,
    PatchReviewerAgent,
    ImportCleanerAgent,
    CommitWriterAgent,
    SecurityExpertAgent,
    PerformanceExpertAgent
)


class TestCodeExpertAgent:
    """Test Code Expert Agent."""
    
    def test_initialization(self, mock_backend):
        """Test agent initialization."""
        agent = CodeExpertAgent(mock_backend)
        assert agent.name == "Code Expert"
        assert agent.description == "Expert in explaining Python code and OpenStack patterns"
        assert agent.backend == mock_backend
    
    def test_system_prompt(self, mock_backend):
        """Test system prompt generation."""
        agent = CodeExpertAgent(mock_backend)
        prompt = agent.get_system_prompt()
        assert "OpenStack" in prompt
        assert "Python" in prompt
        assert "code explanation" in prompt.lower()
    
    def test_user_prompt(self, mock_backend, sample_python_code):
        """Test user prompt generation."""
        agent = CodeExpertAgent(mock_backend)
        prompt = agent.get_user_prompt(sample_python_code)
        assert sample_python_code in prompt
        assert "explain" in prompt.lower()
    
    @pytest.mark.asyncio
    async def test_process(self, mock_backend, sample_python_code):
        """Test agent processing."""
        agent = CodeExpertAgent(mock_backend)
        success, response, error = await agent.process(sample_python_code)
        
        assert success is True
        assert response == "Test response"
        assert error is None
        mock_backend.generate_response.assert_called_once()


class TestSecurityExpertAgent:
    """Test Security Expert Agent."""
    
    def test_initialization(self, mock_backend):
        """Test agent initialization."""
        agent = SecurityExpertAgent(mock_backend)
        assert agent.name == "Security Expert"
        assert "security" in agent.description.lower()
    
    def test_system_prompt(self, mock_backend):
        """Test system prompt generation."""
        agent = SecurityExpertAgent(mock_backend)
        prompt = agent.get_system_prompt()
        assert "security" in prompt.lower()
        assert "vulnerability" in prompt.lower()
        assert "OpenStack" in prompt
    
    def test_user_prompt(self, mock_backend, sample_python_code):
        """Test user prompt generation."""
        agent = SecurityExpertAgent(mock_backend)
        prompt = agent.get_user_prompt(sample_python_code)
        assert sample_python_code in prompt
        assert "security" in prompt.lower()
        assert "vulnerability" in prompt.lower()


class TestPerformanceExpertAgent:
    """Test Performance Expert Agent."""
    
    def test_initialization(self, mock_backend):
        """Test agent initialization."""
        agent = PerformanceExpertAgent(mock_backend)
        assert agent.name == "Performance Expert"
        assert "performance" in agent.description.lower()
    
    def test_system_prompt(self, mock_backend):
        """Test system prompt generation."""
        agent = PerformanceExpertAgent(mock_backend)
        prompt = agent.get_system_prompt()
        assert "performance" in prompt.lower()
        assert "optimization" in prompt.lower()
        assert "OpenStack" in prompt
    
    def test_user_prompt(self, mock_backend, sample_python_code):
        """Test user prompt generation."""
        agent = PerformanceExpertAgent(mock_backend)
        prompt = agent.get_user_prompt(sample_python_code)
        assert sample_python_code in prompt
        assert "performance" in prompt.lower()
        assert "optimization" in prompt.lower()


class TestPatchReviewerAgent:
    """Test Patch Reviewer Agent."""
    
    def test_initialization(self, mock_backend):
        """Test agent initialization."""
        agent = PatchReviewerAgent(mock_backend)
        assert agent.name == "Patch Reviewer"
        assert "patch" in agent.description.lower()
    
    def test_user_prompt(self, mock_backend, sample_diff):
        """Test user prompt generation."""
        agent = PatchReviewerAgent(mock_backend)
        prompt = agent.get_user_prompt(sample_diff)
        assert sample_diff in prompt
        assert "review" in prompt.lower()


class TestImportCleanerAgent:
    """Test Import Cleaner Agent."""
    
    def test_initialization(self, mock_backend):
        """Test agent initialization."""
        agent = ImportCleanerAgent(mock_backend)
        assert agent.name == "Import Cleaner"
        assert "import" in agent.description.lower()
    
    def test_user_prompt(self, mock_backend, sample_python_code):
        """Test user prompt generation."""
        agent = ImportCleanerAgent(mock_backend)
        prompt = agent.get_user_prompt(sample_python_code)
        assert sample_python_code in prompt
        assert "import" in prompt.lower()


class TestCommitWriterAgent:
    """Test Commit Writer Agent."""
    
    def test_initialization(self, mock_backend):
        """Test agent initialization."""
        agent = CommitWriterAgent(mock_backend)
        assert agent.name == "Commit Writer"
        assert "commit" in agent.description.lower()
    
    def test_user_prompt(self, mock_backend, sample_diff):
        """Test user prompt generation."""
        agent = CommitWriterAgent(mock_backend)
        prompt = agent.get_user_prompt(sample_diff)
        assert sample_diff in prompt
        assert "commit" in prompt.lower()


class TestAgentIntegration:
    """Test agent integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_agent_error_handling(self, mock_backend):
        """Test agent error handling."""
        # Mock backend to return error
        mock_backend.generate_response = AsyncMock(return_value=(False, None, "API Error"))
        
        agent = CodeExpertAgent(mock_backend)
        success, response, error = await agent.process("test code")
        
        assert success is False
        assert response is None
        assert error == "API Error"
    
    @pytest.mark.asyncio
    async def test_agent_exception_handling(self, mock_backend):
        """Test agent exception handling."""
        # Mock backend to raise exception
        mock_backend.generate_response = AsyncMock(side_effect=Exception("Network Error"))
        
        agent = CodeExpertAgent(mock_backend)
        success, response, error = await agent.process("test code")
        
        assert success is False
        assert response is None
        assert "Network Error" in error
