"""Integration testing configuration and fixtures."""

import pytest
import tempfile
import os
import asyncio
from unittest.mock import Mock, patch

from explainstack.app import main
from explainstack.agents import CodeExpertAgent, SecurityExpertAgent, PerformanceExpertAgent
from explainstack.backends import OpenAIBackend, ClaudeBackend, GeminiBackend
from explainstack.database import DatabaseManager
from explainstack.auth import AuthService, AuthMiddleware
from explainstack.user import UserService, UserPreferencesManager
from explainstack.utils import FileHandler
from explainstack.integrations import GerritIntegration
from explainstack.analytics import AnalyticsManager


@pytest.fixture
def integration_database():
    """Integration database fixture."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        db_manager = DatabaseManager(db_path)
        yield db_manager
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


@pytest.fixture
def integration_auth_service(integration_database):
    """Integration authentication service fixture."""
    return AuthService(integration_database)


@pytest.fixture
def integration_auth_middleware(integration_auth_service):
    """Integration authentication middleware fixture."""
    return AuthMiddleware(integration_auth_service)


@pytest.fixture
def integration_user_service(integration_database):
    """Integration user service fixture."""
    return UserService(integration_database)


@pytest.fixture
def integration_preferences_manager(integration_database):
    """Integration preferences manager fixture."""
    return UserPreferencesManager(integration_database)


@pytest.fixture
def integration_file_handler():
    """Integration file handler fixture."""
    return FileHandler()


@pytest.fixture
def integration_gerrit():
    """Integration Gerrit fixture."""
    return GerritIntegration()


@pytest.fixture
def integration_analytics():
    """Integration analytics fixture."""
    return AnalyticsManager()


@pytest.fixture
def integration_backends():
    """Integration backends fixture."""
    return {
        'openai': OpenAIBackend({"api_key": "test", "model": "gpt-4"}),
        'claude': ClaudeBackend({"api_key": "test", "model": "claude-3-sonnet"}),
        'gemini': GeminiBackend({"api_key": "test", "model": "gemini-pro"})
    }


@pytest.fixture
def integration_agents(integration_backends):
    """Integration agents fixture."""
    return {
        'code_expert': CodeExpertAgent(integration_backends['openai']),
        'security_expert': SecurityExpertAgent(integration_backends['claude']),
        'performance_expert': PerformanceExpertAgent(integration_backends['gemini'])
    }


@pytest.fixture
def integration_test_user(integration_auth_service):
    """Integration test user fixture."""
    user_id = integration_auth_service.register_user("test@example.com", "password123")
    return {
        'id': user_id,
        'email': "test@example.com",
        'password': "password123"
    }


@pytest.fixture
def integration_test_session(integration_auth_service, integration_test_user):
    """Integration test session fixture."""
    session_id = integration_auth_service.login_user(
        integration_test_user['email'], 
        integration_test_user['password']
    )
    return {
        'id': session_id,
        'user_id': integration_test_user['id']
    }


@pytest.fixture
def integration_test_data():
    """Integration test data fixture."""
    return {
        'python_code': """
def hello_world():
    print("Hello, World!")
    return True

if __name__ == "__main__":
    hello_world()
""",
        'diff_content': """
--- a/test.py
+++ b/test.py
@@ -1,3 +1,3 @@
 def hello_world():
-    print("Hello, World!")
+    print("Hello, Universe!")
""",
        'gerrit_url': "https://review.opendev.org/c/openstack/nova/+/12345",
        'file_content': "print('hello world')",
        'large_file_content': "def test_function():\n" + "    pass\n" * 1000
    }


@pytest.fixture
def integration_mock_chainlit():
    """Integration mock Chainlit fixture."""
    class MockChainlit:
        def __init__(self):
            self.messages = []
            self.user_session = {}
        
        class Message:
            def __init__(self, content):
                self.content = content
            
            async def send(self):
                pass
        
        class user_session:
            def __init__(self):
                self.data = {}
            
            def get(self, key):
                return self.data.get(key)
            
            def set(self, key, value):
                self.data[key] = value
        
        def on_message(self, func):
            return func
        
        def on_chat_start(self, func):
            return func
    
    return MockChainlit()


@pytest.fixture
def integration_workflow():
    """Integration workflow fixture."""
    class IntegrationWorkflow:
        def __init__(self):
            self.steps = []
            self.results = []
        
        def add_step(self, step_name, step_func):
            """Add workflow step."""
            self.steps.append({
                'name': step_name,
                'function': step_func
            })
        
        async def execute(self):
            """Execute workflow."""
            for step in self.steps:
                try:
                    result = await step['function']()
                    self.results.append({
                        'step': step['name'],
                        'success': True,
                        'result': result
                    })
                except Exception as e:
                    self.results.append({
                        'step': step['name'],
                        'success': False,
                        'error': str(e)
                    })
            
            return self.results
        
        def get_results(self):
            """Get workflow results."""
            return self.results
        
        def get_successful_steps(self):
            """Get successful steps."""
            return [r for r in self.results if r['success']]
        
        def get_failed_steps(self):
            """Get failed steps."""
            return [r for r in self.results if not r['success']]
    
    return IntegrationWorkflow()


@pytest.fixture
def integration_test_scenarios():
    """Integration test scenarios fixture."""
    return {
        'user_registration': {
            'email': 'newuser@example.com',
            'password': 'password123'
        },
        'user_login': {
            'email': 'test@example.com',
            'password': 'password123'
        },
        'code_analysis': {
            'input': 'def hello():\n    print("Hello, World!")',
            'expected_agent': 'code_expert'
        },
        'security_analysis': {
            'input': 'import os; os.system("rm -rf /")',
            'expected_agent': 'security_expert'
        },
        'performance_analysis': {
            'input': 'for i in range(1000000):\n    pass',
            'expected_agent': 'performance_expert'
        },
        'file_upload': {
            'filename': 'test.py',
            'content': 'print("hello world")',
            'expected_type': 'python'
        },
        'gerrit_analysis': {
            'url': 'https://review.opendev.org/c/openstack/nova/+/12345',
            'expected_project': 'openstack/nova'
        }
    }


@pytest.fixture
def integration_error_scenarios():
    """Integration error scenarios fixture."""
    return {
        'invalid_email': {
            'email': 'invalid-email',
            'password': 'password123'
        },
        'weak_password': {
            'email': 'test@example.com',
            'password': '123'
        },
        'empty_input': {
            'input': '',
            'expected_error': 'Message cannot be empty'
        },
        'too_long_input': {
            'input': 'x' * 15000,
            'expected_error': 'Message too long'
        },
        'invalid_file_type': {
            'filename': 'test.exe',
            'content': 'binary content',
            'expected_error': 'File type not allowed'
        },
        'malicious_input': {
            'input': '<script>alert("XSS")</script>',
            'expected_sanitization': True
        }
    }


@pytest.fixture
def integration_performance_scenarios():
    """Integration performance scenarios fixture."""
    return {
        'concurrent_users': {
            'user_count': 10,
            'requests_per_user': 5,
            'expected_response_time': 1.0
        },
        'large_file_processing': {
            'file_size': 1024 * 1024,  # 1MB
            'expected_processing_time': 2.0
        },
        'database_operations': {
            'operation_count': 1000,
            'expected_total_time': 5.0
        },
        'memory_usage': {
            'operation_count': 100,
            'expected_memory_increase': 50  # MB
        }
    }


@pytest.fixture
def integration_security_scenarios():
    """Integration security scenarios fixture."""
    return {
        'sql_injection': {
            'input': "'; DROP TABLE users; --",
            'expected_protection': True
        },
        'xss_attempt': {
            'input': '<script>alert("XSS")</script>',
            'expected_sanitization': True
        },
        'path_traversal': {
            'input': '../../../etc/passwd',
            'expected_protection': True
        },
        'command_injection': {
            'input': 'test; rm -rf /',
            'expected_protection': True
        },
        'session_fixation': {
            'session_id': 'fixed_session_id',
            'expected_regeneration': True
        }
    }


@pytest.fixture
def integration_analytics_scenarios():
    """Integration analytics scenarios fixture."""
    return {
        'agent_usage_tracking': {
            'agent_id': 'code_expert',
            'user_id': 'user123',
            'tokens_used': 100,
            'cost': 0.01,
            'response_time': 0.5,
            'success': True
        },
        'user_behavior_tracking': {
            'user_id': 'user123',
            'action': 'code_analysis',
            'timestamp': time.time()
        },
        'performance_metrics': {
            'metric_name': 'response_time',
            'value': 0.5,
            'unit': 'seconds'
        },
        'cost_tracking': {
            'agent_id': 'openai',
            'tokens_used': 1000,
            'cost_per_token': 0.0001,
            'total_cost': 0.1
        }
    }


@pytest.fixture
def integration_test_environment():
    """Integration test environment fixture."""
    class IntegrationTestEnvironment:
        def __init__(self):
            self.services = {}
            self.config = {}
            self.state = {}
        
        def add_service(self, name, service):
            """Add service to environment."""
            self.services[name] = service
        
        def get_service(self, name):
            """Get service from environment."""
            return self.services.get(name)
        
        def set_config(self, key, value):
            """Set configuration."""
            self.config[key] = value
        
        def get_config(self, key):
            """Get configuration."""
            return self.config.get(key)
        
        def set_state(self, key, value):
            """Set state."""
            self.state[key] = value
        
        def get_state(self, key):
            """Get state."""
            return self.state.get(key)
        
        def reset(self):
            """Reset environment."""
            self.services.clear()
            self.config.clear()
            self.state.clear()
    
    return IntegrationTestEnvironment()


@pytest.fixture
def integration_test_runner():
    """Integration test runner fixture."""
    class IntegrationTestRunner:
        def __init__(self):
            self.tests = []
            self.results = []
        
        def add_test(self, test_name, test_func):
            """Add test to runner."""
            self.tests.append({
                'name': test_name,
                'function': test_func
            })
        
        async def run_tests(self):
            """Run all tests."""
            for test in self.tests:
                try:
                    result = await test['function']()
                    self.results.append({
                        'test': test['name'],
                        'success': True,
                        'result': result
                    })
                except Exception as e:
                    self.results.append({
                        'test': test['name'],
                        'success': False,
                        'error': str(e)
                    })
            
            return self.results
        
        def get_results(self):
            """Get test results."""
            return self.results
        
        def get_successful_tests(self):
            """Get successful tests."""
            return [r for r in self.results if r['success']]
        
        def get_failed_tests(self):
            """Get failed tests."""
            return [r for r in self.results if not r['success']]
    
    return IntegrationTestRunner()
