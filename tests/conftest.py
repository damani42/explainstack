"""Pytest configuration and fixtures for ExplainStack tests."""

import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any

# Set test environment
os.environ['TESTING'] = 'true'
os.environ['OPENAI_API_KEY'] = 'test-openai-key'
os.environ['CLAUDE_API_KEY'] = 'test-claude-key'
os.environ['GEMINI_API_KEY'] = 'test-gemini-key'


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_config():
    """Mock configuration for tests."""
    return {
        "backends": {
            "code_expert": {
                "type": "openai",
                "config": {
                    "api_key": "test-key",
                    "model": "gpt-4",
                    "temperature": 0.3,
                    "max_tokens": 2000
                }
            },
            "patch_reviewer": {
                "type": "claude",
                "config": {
                    "api_key": "test-key",
                    "model": "claude-3-sonnet-20240229",
                    "temperature": 0.2,
                    "max_tokens": 3000
                }
            }
        },
        "validation": {
            "max_input_length": 10000,
            "min_input_length": 1
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    }


@pytest.fixture
def mock_backend():
    """Mock backend for tests."""
    backend = Mock()
    backend.name = "test-backend"
    backend.generate_response = AsyncMock(return_value=(True, "Test response", None))
    return backend


@pytest.fixture
def mock_agent():
    """Mock agent for tests."""
    agent = Mock()
    agent.name = "Test Agent"
    agent.description = "Test agent description"
    agent.process = AsyncMock(return_value=(True, "Test response", None))
    return agent


@pytest.fixture
def sample_python_code():
    """Sample Python code for testing."""
    return '''
def calculate_fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

class MathUtils:
    """Utility class for mathematical operations."""
    
    def __init__(self):
        self.cache = {}
    
    def factorial(self, n):
        """Calculate factorial of n."""
        if n in self.cache:
            return self.cache[n]
        if n <= 1:
            result = 1
        else:
            result = n * self.factorial(n-1)
        self.cache[n] = result
        return result
'''


@pytest.fixture
def sample_diff():
    """Sample diff for testing."""
    return '''
diff --git a/nova/compute/manager.py b/nova/compute/manager.py
index 1234567..abcdefg 100644
--- a/nova/compute/manager.py
+++ b/nova/compute/manager.py
@@ -100,6 +100,8 @@ class ComputeManager(manager.Manager):
     def __init__(self, *args, **kwargs):
         super(ComputeManager, self).__init__(*args, **kwargs)
         self.driver = driver.load_compute_driver()
+        # Add quota management
+        self.quota_manager = quota.QuotaManager()
     
     def create_instance(self, context, instance):
         """Create a new instance."""
'''


@pytest.fixture
def sample_gerrit_url():
    """Sample Gerrit URL for testing."""
    return "https://review.opendev.org/c/openstack/nova/+/12345"


@pytest.fixture
def mock_user():
    """Mock user for authentication tests."""
    user = Mock()
    user.id = "test-user-123"
    user.email = "test@example.com"
    user.name = "Test User"
    return user


@pytest.fixture
def mock_session():
    """Mock session for tests."""
    session = Mock()
    session.id = "test-session-123"
    session.user_id = "test-user-123"
    return session
