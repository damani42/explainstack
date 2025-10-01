# 🔌 API Reference

Complete API documentation for ExplainStack.

## 📋 Table of Contents

- [Agents API](#agents-api)
- [Backends API](#backends-api)
- [Authentication API](#authentication-api)
- [Analytics API](#analytics-api)
- [CLI API](#cli-api)
- [Configuration API](#configuration-api)
- [Error Handling](#error-handling)

## 🤖 Agents API

### BaseAgent

Base class for all ExplainStack agents.

```python
from explainstack.agents import BaseAgent

class BaseAgent(ABC):
    """Base class for all ExplainStack agents."""
    
    def __init__(self, name: str, description: str, backend: BaseBackend):
        """Initialize the agent."""
        self.name = name
        self.description = description
        self.backend = backend
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        pass
    
    @abstractmethod
    def get_user_prompt(self, user_input: str) -> str:
        """Get the user prompt for this agent."""
        pass
    
    async def process(self, user_input: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Process user input with this agent."""
        pass
```

### Available Agents

#### CodeExpertAgent
```python
from explainstack.agents import CodeExpertAgent

agent = CodeExpertAgent(backend)
success, response, error = await agent.process("def hello(): print('world')")
```

#### SecurityExpertAgent
```python
from explainstack.agents import SecurityExpertAgent

agent = SecurityExpertAgent(backend)
success, response, error = await agent.process("user_input = request.GET.get('id')")
```

#### PerformanceExpertAgent
```python
from explainstack.agents import PerformanceExpertAgent

agent = PerformanceExpertAgent(backend)
success, response, error = await agent.process("for i in range(1000000): process(i)")
```

#### PatchReviewerAgent
```python
from explainstack.agents import PatchReviewerAgent

agent = PatchReviewerAgent(backend)
success, response, error = await agent.process("diff --git a/file.py b/file.py")
```

#### ImportCleanerAgent
```python
from explainstack.agents import ImportCleanerAgent

agent = ImportCleanerAgent(backend)
success, response, error = await agent.process("import os, sys, json")
```

#### CommitWriterAgent
```python
from explainstack.agents import CommitWriterAgent

agent = CommitWriterAgent(backend)
success, response, error = await agent.process("diff --git a/file.py b/file.py")
```

## 🔧 Backends API

### BaseBackend

Base class for all AI backends.

```python
from explainstack.backends import BaseBackend

class BaseBackend(ABC):
    """Base class for all AI backends."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the backend."""
        self.config = config
    
    @abstractmethod
    async def generate_response(self, system_prompt: str, user_prompt: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Generate response from the AI model."""
        pass
```

### Available Backends

#### OpenAIBackend
```python
from explainstack.backends import OpenAIBackend

config = {
    "api_key": "sk-your-key",
    "model": "gpt-4",
    "temperature": 0.3,
    "max_tokens": 2000
}
backend = OpenAIBackend(config)
```

#### ClaudeBackend
```python
from explainstack.backends import ClaudeBackend

config = {
    "api_key": "sk-ant-your-key",
    "model": "claude-3-sonnet-20240229",
    "temperature": 0.2,
    "max_tokens": 3000
}
backend = ClaudeBackend(config)
```

#### GeminiBackend
```python
from explainstack.backends import GeminiBackend

config = {
    "api_key": "your-gemini-key",
    "model": "gemini-pro",
    "temperature": 0.1,
    "max_tokens": 1000
}
backend = GeminiBackend(config)
```

### BackendFactory
```python
from explainstack.backends import BackendFactory

# Create backend by type
backend = BackendFactory.create_backend("openai", config)
backend = BackendFactory.create_backend("claude", config)
backend = BackendFactory.create_backend("gemini", config)
```

## 🔐 Authentication API

### AuthService
```python
from explainstack.auth import AuthService

auth_service = AuthService(db_manager)

# Register user
success = await auth_service.register_user("user@example.com", "password")

# Login user
session_id = await auth_service.login_user("user@example.com", "password")

# Logout user
await auth_service.logout_user(session_id)

# Get user by session
user = await auth_service.get_user_by_session(session_id)
```

### AuthMiddleware
```python
from explainstack.auth import AuthMiddleware

middleware = AuthMiddleware(auth_service)

# Get current user
user = middleware.get_current_user(session_id)

# Get user configuration
config = middleware.get_user_config(user)
```

### UserService
```python
from explainstack.user import UserService

user_service = UserService(auth_service)

# Get user profile
profile = await user_service.get_user_profile(user_id)

# Update user profile
success = await user_service.update_user_profile(user_id, profile_data)
```

### UserPreferencesManager
```python
from explainstack.user import UserPreferencesManager

preferences_manager = UserPreferencesManager(auth_service)

# Get user preferences
preferences = await preferences_manager.get_user_preferences(user_id)

# Update user preferences
success = await preferences_manager.update_user_preferences(user_id, preferences)
```

## 📊 Analytics API

### AnalyticsManager
```python
from explainstack.analytics import AnalyticsManager

analytics_manager = AnalyticsManager()

# Track user session
analytics_manager.track_user_session(user_id, session_id)

# Track agent usage
analytics_manager.track_agent_usage(
    agent_id="code_expert",
    user_id=user_id,
    tokens_used=150,
    cost=0.01,
    response_time=2.5,
    success=True
)

# Get dashboard data
dashboard_data = analytics_manager.get_dashboard_data(user_id, hours=24)

# Get analytics report
report = analytics_manager.generate_analytics_report(hours=24)
```

### MetricsCollector
```python
from explainstack.analytics import MetricsCollector

metrics_collector = MetricsCollector()

# Get user metrics
user_metrics = metrics_collector.get_user_metrics(user_id)

# Get system metrics
system_metrics = metrics_collector.get_system_metrics(hours=24)

# Get agent performance
agent_performance = metrics_collector.get_agent_performance("code_expert", hours=24)

# Export metrics
exported_data = metrics_collector.export_metrics(format="json")
```

## 🖥️ CLI API

### CLI Commands
```python
from explainstack.cli.commands import AnalyzeCommand, SecurityCommand

# Analyze command
analyze_cmd = AnalyzeCommand(agent_router)
result = analyze_cmd.execute(args)

# Security command
security_cmd = SecurityCommand(agent_router)
result = security_cmd.execute(args)
```

### CLI Main
```python
from explainstack.cli import main

# Run CLI
main()
```

## ⚙️ Configuration API

### AgentConfig
```python
from explainstack.config import AgentConfig

config = get_config()
agent_config = AgentConfig(config)

# Get agent
agent = agent_config.get_agent("code_expert")

# Get all agents
agents = agent_config.get_all_agents()

# Get agent list
agent_list = agent_config.get_agent_list()

# Auto-select agent
agent_id = agent_config.get_auto_agent_id("explain this code")
```

### AgentRouter
```python
from explainstack.config import AgentRouter

router = AgentRouter(agent_config)

# Route request
success, response, error = await router.route_request("user input", "code_expert")

# Get available agents
agents = router.get_available_agents()

# Get auto suggestion
suggestion = router.get_auto_suggestion("user input")
```

## 🔗 Integrations API

### GerritIntegration
```python
from explainstack.integrations import GerritIntegration

gerrit = GerritIntegration()

# Parse Gerrit URL
url_info = gerrit.parse_gerrit_url("https://review.opendev.org/c/openstack/nova/+/12345")

# Analyze Gerrit URL
success, analysis, error = gerrit.analyze_gerrit_url(url)

# Check if URL is Gerrit
is_gerrit = gerrit.is_gerrit_url("https://review.opendev.org/c/...")
```

### OAuth Integration
```python
from explainstack.oauth import OAuthManager

oauth_manager = OAuthManager()

# Get available providers
providers = oauth_manager.get_available_providers()

# Get authorization URL
success, url, error = oauth_manager.get_authorization_url("google", user_id)

# Handle OAuth callback
success, user_data, error = oauth_manager.handle_oauth_callback("google", code, state)
```

## 🛠️ Utilities API

### FileHandler
```python
from explainstack.utils import FileHandler

file_handler = FileHandler()

# Validate file
is_valid, error = file_handler.validate_file(file_path, file_size)

# Save uploaded file
success, file_path, error = file_handler.save_uploaded_file(content, filename)

# Read file content
success, content, error = file_handler.read_file_content(file_path)

# Process file for analysis
success, file_info, error = file_handler.process_file_for_analysis(file_path)
```

## ❌ Error Handling

### Common Error Types

#### Agent Errors
```python
# Agent processing error
success, response, error = await agent.process(input)
if not success:
    print(f"Agent error: {error}")
```

#### Backend Errors
```python
# Backend API error
success, response, error = await backend.generate_response(system, user)
if not success:
    print(f"Backend error: {error}")
```

#### Authentication Errors
```python
# Authentication error
user = auth_service.get_user_by_session(session_id)
if not user:
    print("Authentication failed")
```

#### File Handling Errors
```python
# File validation error
is_valid, error = file_handler.validate_file(file_path, size)
if not is_valid:
    print(f"File error: {error}")
```

### Error Response Format

All API methods return a tuple format:
```python
(success: bool, result: Optional[Any], error: Optional[str])
```

- `success`: Boolean indicating if the operation succeeded
- `result`: The actual result data (None if success=False)
- `error`: Error message (None if success=True)

### Exception Handling

```python
try:
    success, result, error = await agent.process(input)
    if not success:
        # Handle API error
        handle_error(error)
    else:
        # Handle success
        handle_success(result)
except Exception as e:
    # Handle unexpected error
    handle_unexpected_error(e)
```

## 📝 Examples

### Complete Agent Usage
```python
import asyncio
from explainstack.config import get_config, AgentConfig, AgentRouter
from explainstack.backends import BackendFactory

async def analyze_code(code: str):
    # Load configuration
    config = get_config()
    agent_config = AgentConfig(config)
    router = AgentRouter(agent_config)
    
    # Route request
    success, response, error = await router.route_request(code)
    
    if success:
        print(f"Analysis: {response}")
    else:
        print(f"Error: {error}")

# Usage
asyncio.run(analyze_code("def hello(): print('world')"))
```

### CLI Integration
```python
from explainstack.cli.commands import AnalyzeCommand
from explainstack.config import AgentConfig, AgentRouter

# Setup
config = get_config()
agent_config = AgentConfig(config)
router = AgentRouter(agent_config)

# Create command
analyze_cmd = AnalyzeCommand(router)

# Mock args
class Args:
    def __init__(self, file_path):
        self.file = file_path
        self.agent = None

# Execute
args = Args("test.py")
result = analyze_cmd.execute(args)
print(result)
```

### Analytics Integration
```python
from explainstack.analytics import AnalyticsManager

# Initialize
analytics = AnalyticsManager()

# Track usage
analytics.track_agent_usage(
    agent_id="code_expert",
    user_id="user-123",
    tokens_used=150,
    cost=0.01,
    response_time=2.5,
    success=True
)

# Get report
report = analytics.generate_analytics_report(hours=24)
print(report)
```
