"""Tests for ExplainStack CLI."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from explainstack.cli.commands import (
    AnalyzeCommand,
    SecurityCommand,
    ReviewCommand,
    CleanCommand,
    CommitCommand,
    PerformanceCommand
)


class TestAnalyzeCommand:
    """Test Analyze Command."""
    
    @pytest.fixture
    def mock_agent_router(self):
        """Mock agent router."""
        router = Mock()
        router.route_request = AsyncMock(return_value=(True, "Analysis result", None))
        return router
    
    def test_initialization(self, mock_agent_router):
        """Test command initialization."""
        command = AnalyzeCommand(mock_agent_router)
        assert command.agent_router == mock_agent_router
    
    def test_read_file_success(self, mock_agent_router, temp_dir, sample_python_code):
        """Test successful file reading."""
        # Create test file
        test_file = temp_dir / "test.py"
        test_file.write_text(sample_python_code)
        
        command = AnalyzeCommand(mock_agent_router)
        success, content, error = command.read_file(str(test_file))
        
        assert success is True
        assert content == sample_python_code
        assert error is None
    
    def test_read_file_not_found(self, mock_agent_router):
        """Test file not found error."""
        command = AnalyzeCommand(mock_agent_router)
        success, content, error = command.read_file("nonexistent.py")
        
        assert success is False
        assert content is None
        assert "File not found" in error
    
    @pytest.mark.asyncio
    async def test_process_with_agent_success(self, mock_agent_router):
        """Test successful agent processing."""
        command = AnalyzeCommand(mock_agent_router)
        success, result, error = await command.process_with_agent("test code", "code_expert")
        
        assert success is True
        assert result == "Analysis result"
        assert error is None
        mock_agent_router.route_request.assert_called_once_with("test code", "code_expert")
    
    @pytest.mark.asyncio
    async def test_process_with_agent_error(self, mock_agent_router):
        """Test agent processing error."""
        mock_agent_router.route_request = AsyncMock(return_value=(False, None, "Agent error"))
        
        command = AnalyzeCommand(mock_agent_router)
        success, result, error = await command.process_with_agent("test code", "code_expert")
        
        assert success is False
        assert result is None
        assert error == "Agent error"
    
    def test_execute_success(self, mock_agent_router, temp_dir, sample_python_code):
        """Test successful command execution."""
        # Create test file
        test_file = temp_dir / "test.py"
        test_file.write_text(sample_python_code)
        
        # Mock arguments
        args = Mock()
        args.file = str(test_file)
        args.agent = None
        
        command = AnalyzeCommand(mock_agent_router)
        
        with patch('asyncio.new_event_loop') as mock_loop:
            mock_loop.return_value.run_until_complete.return_value = (True, "Analysis result", None)
            result = command.execute(args)
        
        assert "🧠 **Code Analysis**" in result
        assert "Analysis result" in result


class TestSecurityCommand:
    """Test Security Command."""
    
    @pytest.fixture
    def mock_agent_router(self):
        """Mock agent router."""
        router = Mock()
        router.route_request = AsyncMock(return_value=(True, "Security analysis", None))
        return router
    
    def test_execute_success(self, mock_agent_router, temp_dir, sample_python_code):
        """Test successful security command execution."""
        # Create test file
        test_file = temp_dir / "test.py"
        test_file.write_text(sample_python_code)
        
        # Mock arguments
        args = Mock()
        args.file = str(test_file)
        
        command = SecurityCommand(mock_agent_router)
        
        with patch('asyncio.new_event_loop') as mock_loop:
            mock_loop.return_value.run_until_complete.return_value = (True, "Security analysis", None)
            result = command.execute(args)
        
        assert "🔒 **Security Analysis**" in result
        assert "Security analysis" in result


class TestReviewCommand:
    """Test Review Command."""
    
    @pytest.fixture
    def mock_agent_router(self):
        """Mock agent router."""
        router = Mock()
        router.route_request = AsyncMock(return_value=(True, "Patch review", None))
        return router
    
    def test_execute_success(self, mock_agent_router, temp_dir, sample_diff):
        """Test successful review command execution."""
        # Create test file
        test_file = temp_dir / "patch.diff"
        test_file.write_text(sample_diff)
        
        # Mock arguments
        args = Mock()
        args.file = str(test_file)
        
        command = ReviewCommand(mock_agent_router)
        
        with patch('asyncio.new_event_loop') as mock_loop:
            mock_loop.return_value.run_until_complete.return_value = (True, "Patch review", None)
            result = command.execute(args)
        
        assert "🔍 **Patch Review**" in result
        assert "Patch review" in result


class TestCleanCommand:
    """Test Clean Command."""
    
    @pytest.fixture
    def mock_agent_router(self):
        """Mock agent router."""
        router = Mock()
        router.route_request = AsyncMock(return_value=(True, "Import cleaning", None))
        return router
    
    def test_execute_success(self, mock_agent_router, temp_dir, sample_python_code):
        """Test successful clean command execution."""
        # Create test file
        test_file = temp_dir / "test.py"
        test_file.write_text(sample_python_code)
        
        # Mock arguments
        args = Mock()
        args.file = str(test_file)
        
        command = CleanCommand(mock_agent_router)
        
        with patch('asyncio.new_event_loop') as mock_loop:
            mock_loop.return_value.run_until_complete.return_value = (True, "Import cleaning", None)
            result = command.execute(args)
        
        assert "🧹 **Import Cleaning**" in result
        assert "Import cleaning" in result


class TestCommitCommand:
    """Test Commit Command."""
    
    @pytest.fixture
    def mock_agent_router(self):
        """Mock agent router."""
        router = Mock()
        router.route_request = AsyncMock(return_value=(True, "Commit message", None))
        return router
    
    def test_execute_success(self, mock_agent_router, temp_dir, sample_diff):
        """Test successful commit command execution."""
        # Create test file
        test_file = temp_dir / "patch.diff"
        test_file.write_text(sample_diff)
        
        # Mock arguments
        args = Mock()
        args.file = str(test_file)
        
        command = CommitCommand(mock_agent_router)
        
        with patch('asyncio.new_event_loop') as mock_loop:
            mock_loop.return_value.run_until_complete.return_value = (True, "Commit message", None)
            result = command.execute(args)
        
        assert "💬 **Commit Message**" in result
        assert "Commit message" in result


class TestPerformanceCommand:
    """Test Performance Command."""
    
    @pytest.fixture
    def mock_agent_router(self):
        """Mock agent router."""
        router = Mock()
        router.route_request = AsyncMock(return_value=(True, "Performance analysis", None))
        return router
    
    def test_execute_success(self, mock_agent_router, temp_dir, sample_python_code):
        """Test successful performance command execution."""
        # Create test file
        test_file = temp_dir / "test.py"
        test_file.write_text(sample_python_code)
        
        # Mock arguments
        args = Mock()
        args.file = str(test_file)
        
        command = PerformanceCommand(mock_agent_router)
        
        with patch('asyncio.new_event_loop') as mock_loop:
            mock_loop.return_value.run_until_complete.return_value = (True, "Performance analysis", None)
            result = command.execute(args)
        
        assert "⚡ **Performance Analysis**" in result
        assert "Performance analysis" in result


class TestCLIIntegration:
    """Test CLI integration scenarios."""
    
    def test_command_error_handling(self, temp_dir):
        """Test command error handling."""
        # Create test file
        test_file = temp_dir / "test.py"
        test_file.write_text("print('hello')")
        
        # Mock agent router with error
        mock_router = Mock()
        mock_router.route_request = AsyncMock(return_value=(False, None, "Agent error"))
        
        # Mock arguments
        args = Mock()
        args.file = str(test_file)
        
        command = AnalyzeCommand(mock_router)
        
        with patch('asyncio.new_event_loop') as mock_loop:
            mock_loop.return_value.run_until_complete.return_value = (False, None, "Agent error")
            result = command.execute(args)
        
        assert "❌ Error: Agent error" in result
    
    def test_file_encoding_handling(self, temp_dir):
        """Test file encoding handling."""
        # Create test file with special characters
        test_file = temp_dir / "test.py"
        test_file.write_text("# -*- coding: utf-8 -*-\nprint('héllo wörld')")
        
        mock_router = Mock()
        command = AnalyzeCommand(mock_router)
        
        success, content, error = command.read_file(str(test_file))
        
        assert success is True
        assert "héllo wörld" in content
        assert error is None
