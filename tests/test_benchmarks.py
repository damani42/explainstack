"""Benchmark tests for ExplainStack performance."""

import pytest
import time
import asyncio
import psutil
import os
from unittest.mock import Mock, patch
import memory_profiler

from explainstack.agents import CodeExpertAgent, SecurityExpertAgent, PerformanceExpertAgent
from explainstack.backends import OpenAIBackend, ClaudeBackend, GeminiBackend
from explainstack.database import DatabaseManager
from explainstack.auth import AuthService, AuthMiddleware
from explainstack.user import UserService, UserPreferencesManager
from explainstack.utils import FileHandler
from explainstack.analytics import AnalyticsManager


class TestBenchmarks:
    """Benchmark tests for ExplainStack performance."""
    
    @pytest.mark.benchmark
    def test_agent_response_time_benchmark(self):
        """Benchmark agent response times."""
        mock_backend = Mock()
        mock_backend.generate_response.return_value = ("Test response", 100, 0.01)
        
        agent = CodeExpertAgent(mock_backend)
        
        # Benchmark response time
        start_time = time.time()
        success, result, error = asyncio.run(agent.process("test input"))
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Benchmark assertions
        assert response_time < 0.1  # Should respond within 100ms
        assert success is True
        assert result is not None
    
    @pytest.mark.benchmark
    def test_memory_usage_benchmark(self):
        """Benchmark memory usage during operations."""
        mock_backend = Mock()
        mock_backend.generate_response.return_value = ("Test response", 100, 0.01)
        
        agent = CodeExpertAgent(mock_backend)
        
        # Get initial memory
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process multiple requests
        for i in range(100):
            asyncio.run(agent.process(f"test input {i}"))
        
        # Get final memory
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory benchmark assertions
        assert memory_increase < 50  # Should not increase by more than 50MB
        assert memory_increase > 0  # Should use some memory
    
    @pytest.mark.benchmark
    def test_database_operations_benchmark(self):
        """Benchmark database operations."""
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_manager = DatabaseManager(db_path)
            auth_service = AuthService(db_manager)
            
            # Benchmark user creation
            start_time = time.time()
            for i in range(1000):
                auth_service.register_user(f"user{i}@test.com", "password123")
            end_time = time.time()
            
            total_time = end_time - start_time
            avg_time = total_time / 1000
            
            # Database benchmark assertions
            assert total_time < 10.0  # Should complete within 10 seconds
            assert avg_time < 0.01  # Average time per operation should be < 10ms
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    @pytest.mark.benchmark
    def test_concurrent_processing_benchmark(self):
        """Benchmark concurrent processing performance."""
        mock_backend = Mock()
        mock_backend.generate_response.return_value = ("Test response", 100, 0.01)
        
        agent = CodeExpertAgent(mock_backend)
        
        async def process_request(request_id):
            return await agent.process(f"test input {request_id}")
        
        # Benchmark concurrent processing
        start_time = time.time()
        tasks = [process_request(i) for i in range(10)]
        results = asyncio.run(asyncio.gather(*tasks))
        end_time = time.time()
        
        total_time = end_time - start_time
        
        # Concurrent processing benchmark assertions
        assert total_time < 1.0  # Should complete within 1 second
        assert len(results) == 10  # All requests should complete
        
        # Verify all results are successful
        for success, result, error in results:
            assert success is True
            assert result is not None
    
    @pytest.mark.benchmark
    def test_file_processing_benchmark(self):
        """Benchmark file processing performance."""
        file_handler = FileHandler()
        
        # Create large file content
        large_content = "def test_function():\n" * 1000 + "    pass\n" * 1000
        
        # Benchmark file processing
        start_time = time.time()
        success, result, error = file_handler.process_file_for_analysis(
            "large_file.py", large_content
        )
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # File processing benchmark assertions
        assert processing_time < 0.5  # Should process within 500ms
        assert success is True
        assert result is not None
        assert result['lines'] > 0
    
    @pytest.mark.benchmark
    def test_analytics_benchmark(self):
        """Benchmark analytics data collection."""
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            analytics_manager = AnalyticsManager()
            
            # Benchmark analytics tracking
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
            avg_time = total_time / 1000
            
            # Analytics benchmark assertions
            assert total_time < 5.0  # Should complete within 5 seconds
            assert avg_time < 0.005  # Average time per operation should be < 5ms
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    @pytest.mark.benchmark
    def test_backend_performance_benchmark(self):
        """Benchmark backend performance."""
        backends = [
            OpenAIBackend({"api_key": "test", "model": "gpt-4"}),
            ClaudeBackend({"api_key": "test", "model": "claude-3-sonnet"}),
            GeminiBackend({"api_key": "test", "model": "gemini-pro"})
        ]
        
        for backend in backends:
            # Mock API calls
            with patch.object(backend, '_make_api_call') as mock_call:
                mock_call.return_value = ("Test response", 100, 0.01)
                
                # Benchmark backend response
                start_time = time.time()
                success, result, error = asyncio.run(
                    backend.generate_response("test prompt", "test system prompt")
                )
                end_time = time.time()
                
                response_time = end_time - start_time
                
                # Backend benchmark assertions
                assert response_time < 0.1  # Should respond within 100ms
                assert success is True
                assert result is not None
    
    @pytest.mark.benchmark
    def test_memory_profiling_benchmark(self):
        """Benchmark memory usage with profiling."""
        mock_backend = Mock()
        mock_backend.generate_response.return_value = ("Test response", 100, 0.01)
        
        agent = CodeExpertAgent(mock_backend)
        
        # Profile memory usage
        @memory_profiler.profile
        def process_requests():
            for i in range(100):
                asyncio.run(agent.process(f"test input {i}"))
        
        # Run memory profiling
        process_requests()
        
        # Memory profiling assertions
        # This would test that memory usage is within acceptable limits
        # The actual assertions would depend on the profiling results
    
    @pytest.mark.benchmark
    def test_cpu_usage_benchmark(self):
        """Benchmark CPU usage during operations."""
        mock_backend = Mock()
        mock_backend.generate_response.return_value = ("Test response", 100, 0.01)
        
        agent = CodeExpertAgent(mock_backend)
        
        # Get initial CPU usage
        process = psutil.Process(os.getpid())
        initial_cpu = process.cpu_percent()
        
        # Process requests
        start_time = time.time()
        for i in range(100):
            asyncio.run(agent.process(f"test input {i}"))
        end_time = time.time()
        
        # Get final CPU usage
        final_cpu = process.cpu_percent()
        total_time = end_time - start_time
        
        # CPU benchmark assertions
        assert total_time < 5.0  # Should complete within 5 seconds
        # CPU usage assertions would depend on the specific requirements
    
    @pytest.mark.benchmark
    def test_throughput_benchmark(self):
        """Benchmark system throughput."""
        mock_backend = Mock()
        mock_backend.generate_response.return_value = ("Test response", 100, 0.01)
        
        agent = CodeExpertAgent(mock_backend)
        
        # Benchmark throughput
        start_time = time.time()
        request_count = 100
        
        for i in range(request_count):
            asyncio.run(agent.process(f"test input {i}"))
        
        end_time = time.time()
        
        total_time = end_time - start_time
        throughput = request_count / total_time  # requests per second
        
        # Throughput benchmark assertions
        assert throughput > 10  # Should handle at least 10 requests per second
        assert total_time < 10.0  # Should complete within 10 seconds
    
    @pytest.mark.benchmark
    def test_latency_benchmark(self):
        """Benchmark system latency."""
        mock_backend = Mock()
        mock_backend.generate_response.return_value = ("Test response", 100, 0.01)
        
        agent = CodeExpertAgent(mock_backend)
        
        # Benchmark latency
        latencies = []
        for i in range(100):
            start_time = time.time()
            asyncio.run(agent.process(f"test input {i}"))
            end_time = time.time()
            
            latency = end_time - start_time
            latencies.append(latency)
        
        # Calculate latency statistics
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        min_latency = min(latencies)
        
        # Latency benchmark assertions
        assert avg_latency < 0.1  # Average latency should be < 100ms
        assert max_latency < 0.5  # Maximum latency should be < 500ms
        assert min_latency > 0  # Minimum latency should be > 0
    
    @pytest.mark.benchmark
    def test_scalability_benchmark(self):
        """Benchmark system scalability."""
        mock_backend = Mock()
        mock_backend.generate_response.return_value = ("Test response", 100, 0.01)
        
        agent = CodeExpertAgent(mock_backend)
        
        # Test scalability with increasing load
        for load in [10, 50, 100, 200]:
            start_time = time.time()
            
            async def process_request(request_id):
                return await agent.process(f"test input {request_id}")
            
            tasks = [process_request(i) for i in range(load)]
            results = asyncio.run(asyncio.gather(*tasks))
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Scalability benchmark assertions
            assert total_time < load * 0.1  # Should scale linearly
            assert len(results) == load  # All requests should complete
            
            # Verify all results are successful
            for success, result, error in results:
                assert success is True
                assert result is not None
