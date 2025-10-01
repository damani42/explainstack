"""Performance tests for ExplainStack."""

import pytest
import time
import asyncio
from unittest.mock import Mock, patch
import memory_profiler
import psutil
import os

from explainstack.agents import CodeExpertAgent, SecurityExpertAgent, PerformanceExpertAgent
from explainstack.backends import OpenAIBackend, ClaudeBackend, GeminiBackend


class TestPerformance:
    """Performance tests for ExplainStack components."""
    
    @pytest.mark.performance
    def test_agent_response_time(self):
        """Test agent response time under normal conditions."""
        # Mock backend
        mock_backend = Mock()
        mock_backend.generate_response.return_value = ("Test response", 100, 0.01)
        
        # Test different agents
        agents = [
            CodeExpertAgent(mock_backend),
            SecurityExpertAgent(mock_backend),
            PerformanceExpertAgent(mock_backend)
        ]
        
        for agent in agents:
            start_time = time.time()
            success, result, error = asyncio.run(agent.process("test input"))
            end_time = time.time()
            
            response_time = end_time - start_time
            assert response_time < 1.0  # Should respond within 1 second
            assert success is True
            assert result is not None
    
    @pytest.mark.performance
    def test_memory_usage(self):
        """Test memory usage during agent processing."""
        mock_backend = Mock()
        mock_backend.generate_response.return_value = ("Test response", 100, 0.01)
        
        agent = CodeExpertAgent(mock_backend)
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process multiple requests
        for i in range(10):
            asyncio.run(agent.process(f"test input {i}"))
        
        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (< 50MB)
        assert memory_increase < 50
    
    @pytest.mark.performance
    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        mock_backend = Mock()
        mock_backend.generate_response.return_value = ("Test response", 100, 0.01)
        
        agent = CodeExpertAgent(mock_backend)
        
        async def process_request(request_id):
            return await agent.process(f"test input {request_id}")
        
        # Run 5 concurrent requests
        start_time = time.time()
        tasks = [process_request(i) for i in range(5)]
        results = asyncio.run(asyncio.gather(*tasks))
        end_time = time.time()
        
        total_time = end_time - start_time
        
        # All requests should complete successfully
        for success, result, error in results:
            assert success is True
            assert result is not None
        
        # Concurrent processing should be faster than sequential
        assert total_time < 5.0  # Should complete within 5 seconds
    
    @pytest.mark.performance
    def test_large_input_handling(self):
        """Test handling of large input files."""
        mock_backend = Mock()
        mock_backend.generate_response.return_value = ("Test response", 100, 0.01)
        
        agent = CodeExpertAgent(mock_backend)
        
        # Create large input (simulate large Python file)
        large_input = "def test_function():\n" * 1000 + "    pass\n" * 1000
        
        start_time = time.time()
        success, result, error = asyncio.run(agent.process(large_input))
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Should handle large input within reasonable time
        assert response_time < 2.0
        assert success is True
        assert result is not None
    
    @pytest.mark.performance
    def test_backend_performance(self):
        """Test backend performance characteristics."""
        backends = [
            OpenAIBackend({"api_key": "test", "model": "gpt-4"}),
            ClaudeBackend({"api_key": "test", "model": "claude-3-sonnet"}),
            GeminiBackend({"api_key": "test", "model": "gemini-pro"})
        ]
        
        for backend in backends:
            # Mock the actual API calls
            with patch.object(backend, '_make_api_call') as mock_call:
                mock_call.return_value = ("Test response", 100, 0.01)
                
                start_time = time.time()
                success, result, error = asyncio.run(
                    backend.generate_response("test prompt", "test system prompt")
                )
                end_time = time.time()
                
                response_time = end_time - start_time
                
                # Backend should respond quickly
                assert response_time < 0.5
                assert success is True
                assert result is not None
    
    @pytest.mark.performance
    def test_database_performance(self):
        """Test database operations performance."""
        from explainstack.database import DatabaseManager
        
        # Mock database operations
        with patch('explainstack.database.DatabaseManager') as mock_db:
            mock_db.return_value.get_user.return_value = None
            mock_db.return_value.create_user.return_value = True
            
            db_manager = DatabaseManager(":memory:")
            
            # Test user creation performance
            start_time = time.time()
            for i in range(100):
                db_manager.create_user(f"user{i}@test.com", "password")
            end_time = time.time()
            
            total_time = end_time - start_time
            
            # Should handle 100 user creations quickly
            assert total_time < 1.0
    
    @pytest.mark.performance
    def test_file_processing_performance(self):
        """Test file processing performance."""
        from explainstack.utils import FileHandler
        
        file_handler = FileHandler()
        
        # Create test file content
        test_content = "print('hello world')\n" * 1000
        
        start_time = time.time()
        success, result, error = file_handler.process_file_for_analysis(
            "test.py", test_content
        )
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # File processing should be fast
        assert processing_time < 0.5
        assert success is True
        assert result is not None
    
    @pytest.mark.performance
    def test_analytics_performance(self):
        """Test analytics data collection performance."""
        from explainstack.analytics import AnalyticsManager
        
        analytics_manager = AnalyticsManager()
        
        # Mock database operations
        with patch.object(analytics_manager, 'metrics_collector') as mock_collector:
            mock_collector.track_agent_usage.return_value = True
            
            start_time = time.time()
            for i in range(1000):
                analytics_manager.track_agent_usage(
                    agent_id="test_agent",
                    user_id=f"user{i}",
                    tokens_used=100,
                    cost=0.01,
                    response_time=0.5,
                    success=True
                )
            end_time = time.time()
            
            total_time = end_time - start_time
            
            # Should handle 1000 analytics events quickly
            assert total_time < 2.0
    
    @pytest.mark.performance
    def test_memory_leaks(self):
        """Test for memory leaks in long-running operations."""
        mock_backend = Mock()
        mock_backend.generate_response.return_value = ("Test response", 100, 0.01)
        
        agent = CodeExpertAgent(mock_backend)
        
        # Get initial memory
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run many operations
        for i in range(100):
            asyncio.run(agent.process(f"test input {i}"))
            
            # Check memory every 10 iterations
            if i % 10 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = current_memory - initial_memory
                
                # Memory should not grow excessively
                assert memory_increase < 100  # Less than 100MB increase
    
    @pytest.mark.performance
    def test_error_handling_performance(self):
        """Test performance of error handling paths."""
        mock_backend = Mock()
        mock_backend.generate_response.side_effect = Exception("API Error")
        
        agent = CodeExpertAgent(mock_backend)
        
        start_time = time.time()
        success, result, error = asyncio.run(agent.process("test input"))
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Error handling should be fast
        assert response_time < 0.1
        assert success is False
        assert error is not None
