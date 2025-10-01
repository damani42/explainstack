"""Benchmark testing configuration and fixtures."""

import pytest
import time
import psutil
import os
import asyncio
from unittest.mock import Mock, patch
import memory_profiler
import line_profiler

from explainstack.agents import CodeExpertAgent, SecurityExpertAgent, PerformanceExpertAgent
from explainstack.backends import OpenAIBackend, ClaudeBackend, GeminiBackend
from explainstack.database import DatabaseManager
from explainstack.auth import AuthService, AuthMiddleware
from explainstack.user import UserService, UserPreferencesManager
from explainstack.utils import FileHandler
from explainstack.analytics import AnalyticsManager


@pytest.fixture
def benchmark_metrics():
    """Benchmark metrics fixture."""
    class BenchmarkMetrics:
        def __init__(self):
            self.metrics = {
                'response_times': [],
                'memory_usage': [],
                'cpu_usage': [],
                'throughput': 0,
                'error_count': 0,
                'success_count': 0
            }
        
        def record_response_time(self, response_time):
            """Record response time."""
            self.metrics['response_times'].append(response_time)
        
        def record_memory_usage(self, memory_usage):
            """Record memory usage."""
            self.metrics['memory_usage'].append(memory_usage)
        
        def record_cpu_usage(self, cpu_usage):
            """Record CPU usage."""
            self.metrics['cpu_usage'].append(cpu_usage)
        
        def record_success(self):
            """Record successful operation."""
            self.metrics['success_count'] += 1
        
        def record_error(self):
            """Record error."""
            self.metrics['error_count'] += 1
        
        def calculate_throughput(self, total_operations, total_time):
            """Calculate throughput."""
            self.metrics['throughput'] = total_operations / total_time
        
        def get_average_response_time(self):
            """Get average response time."""
            if not self.metrics['response_times']:
                return 0
            return sum(self.metrics['response_times']) / len(self.metrics['response_times'])
        
        def get_max_response_time(self):
            """Get maximum response time."""
            if not self.metrics['response_times']:
                return 0
            return max(self.metrics['response_times'])
        
        def get_min_response_time(self):
            """Get minimum response time."""
            if not self.metrics['response_times']:
                return 0
            return min(self.metrics['response_times'])
        
        def get_average_memory_usage(self):
            """Get average memory usage."""
            if not self.metrics['memory_usage']:
                return 0
            return sum(self.metrics['memory_usage']) / len(self.metrics['memory_usage'])
        
        def get_average_cpu_usage(self):
            """Get average CPU usage."""
            if not self.metrics['cpu_usage']:
                return 0
            return sum(self.metrics['cpu_usage']) / len(self.metrics['cpu_usage'])
        
        def get_success_rate(self):
            """Get success rate."""
            total = self.metrics['success_count'] + self.metrics['error_count']
            if total == 0:
                return 0
            return self.metrics['success_count'] / total
        
        def get_metrics(self):
            """Get all metrics."""
            return self.metrics
    
    return BenchmarkMetrics()


@pytest.fixture
def benchmark_profiler():
    """Benchmark profiler fixture."""
    class BenchmarkProfiler:
        def __init__(self):
            self.profiles = []
        
        def profile_function(self, func, *args, **kwargs):
            """Profile a function."""
            start_time = time.time()
            start_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
            start_cpu = psutil.Process(os.getpid()).cpu_percent()
            
            result = func(*args, **kwargs)
            
            end_time = time.time()
            end_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
            end_cpu = psutil.Process(os.getpid()).cpu_percent()
            
            profile = {
                'function': func.__name__,
                'execution_time': end_time - start_time,
                'memory_usage': end_memory - start_memory,
                'cpu_usage': end_cpu - start_cpu,
                'result': result,
                'timestamp': time.time()
            }
            
            self.profiles.append(profile)
            return result
        
        async def profile_async_function(self, func, *args, **kwargs):
            """Profile an async function."""
            start_time = time.time()
            start_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
            start_cpu = psutil.Process(os.getpid()).cpu_percent()
            
            result = await func(*args, **kwargs)
            
            end_time = time.time()
            end_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
            end_cpu = psutil.Process(os.getpid()).cpu_percent()
            
            profile = {
                'function': func.__name__,
                'execution_time': end_time - start_time,
                'memory_usage': end_memory - start_memory,
                'cpu_usage': end_cpu - start_cpu,
                'result': result,
                'timestamp': time.time()
            }
            
            self.profiles.append(profile)
            return result
        
        def get_profiles(self):
            """Get all profiles."""
            return self.profiles
        
        def get_average_execution_time(self, function_name):
            """Get average execution time for a function."""
            function_profiles = [p for p in self.profiles if p['function'] == function_name]
            if not function_profiles:
                return 0
            
            total_time = sum(p['execution_time'] for p in function_profiles)
            return total_time / len(function_profiles)
        
        def get_memory_usage_by_function(self, function_name):
            """Get memory usage by function."""
            function_profiles = [p for p in self.profiles if p['function'] == function_name]
            if not function_profiles:
                return 0
            
            total_memory = sum(p['memory_usage'] for p in function_profiles)
            return total_memory / len(function_profiles)
    
    return BenchmarkProfiler()


@pytest.fixture
def benchmark_load_tester():
    """Benchmark load tester fixture."""
    class BenchmarkLoadTester:
        def __init__(self):
            self.load_tests = []
        
        async def run_load_test(self, func, concurrent_requests=10, total_requests=100):
            """Run load test."""
            start_time = time.time()
            results = []
            
            # Create batches of concurrent requests
            for batch_start in range(0, total_requests, concurrent_requests):
                batch_end = min(batch_start + concurrent_requests, total_requests)
                batch_size = batch_end - batch_start
                
                # Create concurrent tasks
                tasks = [func() for _ in range(batch_size)]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Record batch results
                batch_time = time.time()
                results.append({
                    'batch_start': batch_start,
                    'batch_size': batch_size,
                    'batch_time': batch_time,
                    'results': batch_results
                })
            
            end_time = time.time()
            total_time = end_time - start_time
            
            load_test_result = {
                'total_requests': total_requests,
                'concurrent_requests': concurrent_requests,
                'total_time': total_time,
                'requests_per_second': total_requests / total_time,
                'results': results
            }
            
            self.load_tests.append(load_test_result)
            return load_test_result
        
        def get_load_tests(self):
            """Get all load tests."""
            return self.load_tests
        
        def get_average_requests_per_second(self):
            """Get average requests per second."""
            if not self.load_tests:
                return 0
            
            total_rps = sum(lt['requests_per_second'] for lt in self.load_tests)
            return total_rps / len(self.load_tests)
    
    return BenchmarkLoadTester()


@pytest.fixture
def benchmark_memory_profiler():
    """Benchmark memory profiler fixture."""
    class BenchmarkMemoryProfiler:
        def __init__(self):
            self.snapshots = []
        
        def take_snapshot(self, label=""):
            """Take memory snapshot."""
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            snapshot = {
                'label': label,
                'timestamp': time.time(),
                'rss': memory_info.rss / 1024 / 1024,  # MB
                'vms': memory_info.vms / 1024 / 1024,  # MB
                'percent': process.memory_percent()
            }
            
            self.snapshots.append(snapshot)
            return snapshot
        
        def get_memory_growth(self):
            """Calculate memory growth."""
            if len(self.snapshots) < 2:
                return 0
            
            first = self.snapshots[0]
            last = self.snapshots[-1]
            
            return last['rss'] - first['rss']
        
        def get_memory_peak(self):
            """Get memory peak."""
            if not self.snapshots:
                return 0
            
            return max(s['rss'] for s in self.snapshots)
        
        def get_memory_average(self):
            """Get memory average."""
            if not self.snapshots:
                return 0
            
            total_memory = sum(s['rss'] for s in self.snapshots)
            return total_memory / len(self.snapshots)
        
        def get_snapshots(self):
            """Get all snapshots."""
            return self.snapshots
    
    return BenchmarkMemoryProfiler()


@pytest.fixture
def benchmark_cpu_profiler():
    """Benchmark CPU profiler fixture."""
    class BenchmarkCPUProfiler:
        def __init__(self):
            self.samples = []
        
        def sample(self, label=""):
            """Take CPU sample."""
            process = psutil.Process(os.getpid())
            cpu_percent = process.cpu_percent()
            
            sample = {
                'label': label,
                'timestamp': time.time(),
                'cpu_percent': cpu_percent
            }
            
            self.samples.append(sample)
            return sample
        
        def get_average_cpu(self):
            """Get average CPU usage."""
            if not self.samples:
                return 0
            
            total_cpu = sum(s['cpu_percent'] for s in self.samples)
            return total_cpu / len(self.samples)
        
        def get_cpu_peak(self):
            """Get CPU peak."""
            if not self.samples:
                return 0
            
            return max(s['cpu_percent'] for s in self.samples)
        
        def get_samples(self):
            """Get all samples."""
            return self.samples
    
    return BenchmarkCPUProfiler()


@pytest.fixture
def benchmark_network_profiler():
    """Benchmark network profiler fixture."""
    class BenchmarkNetworkProfiler:
        def __init__(self):
            self.samples = []
        
        def sample(self, label=""):
            """Take network sample."""
            # This would sample network usage if implemented
            sample = {
                'label': label,
                'timestamp': time.time(),
                'bytes_sent': 0,
                'bytes_received': 0
            }
            
            self.samples.append(sample)
            return sample
        
        def get_total_bytes_sent(self):
            """Get total bytes sent."""
            if not self.samples:
                return 0
            
            return sum(s['bytes_sent'] for s in self.samples)
        
        def get_total_bytes_received(self):
            """Get total bytes received."""
            if not self.samples:
                return 0
            
            return sum(s['bytes_received'] for s in self.samples)
        
        def get_samples(self):
            """Get all samples."""
            return self.samples
    
    return BenchmarkNetworkProfiler()


@pytest.fixture
def benchmark_database_profiler():
    """Benchmark database profiler fixture."""
    class BenchmarkDatabaseProfiler:
        def __init__(self):
            self.queries = []
        
        def log_query(self, query, execution_time, rows_affected=0):
            """Log database query."""
            query_log = {
                'query': query,
                'execution_time': execution_time,
                'rows_affected': rows_affected,
                'timestamp': time.time()
            }
            
            self.queries.append(query_log)
            return query_log
        
        def get_average_execution_time(self):
            """Get average query execution time."""
            if not self.queries:
                return 0
            
            total_time = sum(q['execution_time'] for q in self.queries)
            return total_time / len(self.queries)
        
        def get_slowest_query(self):
            """Get slowest query."""
            if not self.queries:
                return None
            
            return max(self.queries, key=lambda q: q['execution_time'])
        
        def get_total_execution_time(self):
            """Get total execution time."""
            if not self.queries:
                return 0
            
            return sum(q['execution_time'] for q in self.queries)
        
        def get_queries(self):
            """Get all queries."""
            return self.queries
    
    return BenchmarkDatabaseProfiler()


@pytest.fixture
def benchmark_agent_tester():
    """Benchmark agent tester fixture."""
    class BenchmarkAgentTester:
        def __init__(self):
            self.agent_tests = []
        
        async def test_agent_performance(self, agent, input_text, iterations=10):
            """Test agent performance."""
            start_time = time.time()
            results = []
            
            for i in range(iterations):
                iteration_start = time.time()
                success, result, error = await agent.process(input_text)
                iteration_end = time.time()
                
                results.append({
                    'iteration': i,
                    'success': success,
                    'result': result,
                    'error': error,
                    'execution_time': iteration_end - iteration_start
                })
            
            end_time = time.time()
            total_time = end_time - start_time
            
            agent_test_result = {
                'agent': agent.__class__.__name__,
                'input_text': input_text,
                'iterations': iterations,
                'total_time': total_time,
                'average_time': total_time / iterations,
                'results': results
            }
            
            self.agent_tests.append(agent_test_result)
            return agent_test_result
        
        def get_agent_tests(self):
            """Get all agent tests."""
            return self.agent_tests
        
        def get_average_agent_time(self, agent_name):
            """Get average time for an agent."""
            agent_results = [at for at in self.agent_tests if at['agent'] == agent_name]
            if not agent_results:
                return 0
            
            total_time = sum(at['average_time'] for at in agent_results)
            return total_time / len(agent_results)
    
    return BenchmarkAgentTester()


@pytest.fixture
def benchmark_backend_tester():
    """Benchmark backend tester fixture."""
    class BenchmarkBackendTester:
        def __init__(self):
            self.backend_tests = []
        
        async def test_backend_performance(self, backend, prompt, system_prompt, iterations=10):
            """Test backend performance."""
            start_time = time.time()
            results = []
            
            for i in range(iterations):
                iteration_start = time.time()
                success, result, error = await backend.generate_response(prompt, system_prompt)
                iteration_end = time.time()
                
                results.append({
                    'iteration': i,
                    'success': success,
                    'result': result,
                    'error': error,
                    'execution_time': iteration_end - iteration_start
                })
            
            end_time = time.time()
            total_time = end_time - start_time
            
            backend_test_result = {
                'backend': backend.__class__.__name__,
                'prompt': prompt,
                'system_prompt': system_prompt,
                'iterations': iterations,
                'total_time': total_time,
                'average_time': total_time / iterations,
                'results': results
            }
            
            self.backend_tests.append(backend_test_result)
            return backend_test_result
        
        def get_backend_tests(self):
            """Get all backend tests."""
            return self.backend_tests
        
        def get_average_backend_time(self, backend_name):
            """Get average time for a backend."""
            backend_results = [bt for bt in self.backend_tests if bt['backend'] == backend_name]
            if not backend_results:
                return 0
            
            total_time = sum(bt['average_time'] for bt in backend_results)
            return total_time / len(backend_results)
    
    return BenchmarkBackendTester()


@pytest.fixture
def benchmark_scalability_tester():
    """Benchmark scalability tester fixture."""
    class BenchmarkScalabilityTester:
        def __init__(self):
            self.scalability_tests = []
        
        async def test_scalability(self, func, load_levels=[10, 50, 100, 200]):
            """Test scalability with increasing load."""
            for load in load_levels:
                start_time = time.time()
                
                # Create concurrent tasks
                tasks = [func() for _ in range(load)]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                end_time = time.time()
                total_time = end_time - start_time
                
                scalability_result = {
                    'load': load,
                    'total_time': total_time,
                    'requests_per_second': load / total_time,
                    'results': results
                }
                
                self.scalability_tests.append(scalability_result)
            
            return self.scalability_tests
        
        def get_scalability_tests(self):
            """Get all scalability tests."""
            return self.scalability_tests
        
        def get_scalability_curve(self):
            """Get scalability curve."""
            if not self.scalability_tests:
                return []
            
            return [
                {
                    'load': st['load'],
                    'requests_per_second': st['requests_per_second']
                }
                for st in self.scalability_tests
            ]
    
    return BenchmarkScalabilityTester()
