# 👨‍💻 Developer Guide

Complete guide for ExplainStack developers and contributors.

## 📋 Table of Contents

- [Development Setup](#development-setup)
- [Architecture Overview](#architecture-overview)
- [Adding New Agents](#adding-new-agents)
- [Adding New Backends](#adding-new-backends)
- [Testing](#testing)
- [Code Style](#code-style)
- [Deployment](#deployment)
- [Contributing](#contributing)

## 🚀 Development Setup

### Prerequisites

- Python 3.8+
- Git
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-username/explainstack.git
cd explainstack
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

4. **Install in development mode**
```bash
pip install -e .
```

### Environment Configuration

1. **Copy environment file**
```bash
cp env.example .env
```

2. **Configure environment variables**
```bash
# Required API keys (at least one)
OPENAI_API_KEY=sk-your-openai-key
CLAUDE_API_KEY=sk-ant-your-claude-key
GEMINI_API_KEY=your-gemini-key

# Optional configuration
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///explainstack.db
```

### Development Tools

```bash
# Install development tools
pip install pytest pytest-cov black flake8 mypy

# Run tests
python run_tests.py

# Run specific tests
python run_tests.py test_agents.py

# Format code
black explainstack/

# Lint code
flake8 explainstack/

# Type checking
mypy explainstack/
```

## 🏗️ Architecture Overview

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │   CLI Interface │    │   API Interface │
│   (Chainlit)    │    │   (Click)       │    │   (FastAPI)     │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │     Agent Router          │
                    │   (Intent Detection)       │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │     Agent System          │
                    │  (Code, Security, etc.)   │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │     Backend System        │
                    │ (OpenAI, Claude, Gemini)  │
                    └───────────────────────────┘
```

### Module Structure

```
explainstack/
├── agents/           # AI agents (Code, Security, etc.)
├── backends/         # AI backends (OpenAI, Claude, Gemini)
├── auth/            # Authentication system
├── analytics/       # Analytics and metrics
├── integrations/    # External integrations (Gerrit, OAuth)
├── cli/             # Command-line interface
├── config/          # Configuration and routing
├── database/        # Database models and management
├── oauth/           # OAuth providers
├── ui/              # User interface components
├── user/            # User management
└── utils/           # Utility functions
```

### Data Flow

1. **Input Processing**
   - User input received (web/CLI/API)
   - Input validation and sanitization
   - Intent detection and agent selection

2. **Agent Processing**
   - Agent receives input and context
   - System and user prompts generated
   - Backend API called with prompts

3. **Response Generation**
   - AI model generates response
   - Response formatted and validated
   - Analytics and metrics recorded

4. **Output Delivery**
   - Response sent to user
   - Session state updated
   - Logging and monitoring

## 🤖 Adding New Agents

### 1. Create Agent Class

```python
# explainstack/agents/new_agent.py
from .base_agent import BaseAgent

class NewAgent(BaseAgent):
    """New specialized agent."""
    
    def __init__(self, backend):
        super().__init__(
            name="New Agent",
            description="Description of what this agent does",
            backend=backend
        )
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        return """You are a specialized agent for [specific task].
        
        Your expertise includes:
        - [Expertise area 1]
        - [Expertise area 2]
        - [Expertise area 3]
        
        Your task is to [specific task description]."""
    
    def get_user_prompt(self, user_input: str) -> str:
        """Get the user prompt for this agent."""
        return f"""Please [specific task] for this input:

```python
{user_input}
```

Provide your analysis in the following structure:
- **Summary**: [Brief summary]
- **Analysis**: [Detailed analysis]
- **Recommendations**: [Specific recommendations]
- **Examples**: [Code examples if applicable]"""
```

### 2. Register Agent

```python
# explainstack/agents/__init__.py
from .new_agent import NewAgent

__all__ = [
    'BaseAgent',
    'CodeExpertAgent',
    # ... other agents
    'NewAgent'
]
```

### 3. Add to Configuration

```python
# explainstack/config.py
DEFAULT_CONFIG = {
    "backends": {
        # ... existing backends
        "new_agent": {
            "type": "openai",  # or "claude", "gemini"
            "config": {
                "api_key": "",
                "model": "gpt-4",
                "temperature": 0.3,
                "max_tokens": 2000
            }
        }
    }
}
```

### 4. Add to Agent Config

```python
# explainstack/config/agent_config.py
from ..agents import NewAgent

def _initialize_agents(self):
    # ... existing agents
    "new_agent": self._create_agent_with_backend(
        "new_agent", NewAgent, backends_config
    ),
```

### 5. Add Intent Detection

```python
# explainstack/config/agent_config.py
def get_auto_agent_id(self, user_input: str) -> str:
    text = user_input.lower()
    
    # New agent detection
    if any(keyword in text for keyword in ["new_task", "specific_keyword"]):
        return "new_agent"
    
    # ... existing detection logic
```

### 6. Add Tests

```python
# tests/test_new_agent.py
import pytest
from explainstack.agents import NewAgent

class TestNewAgent:
    def test_initialization(self, mock_backend):
        agent = NewAgent(mock_backend)
        assert agent.name == "New Agent"
    
    def test_system_prompt(self, mock_backend):
        agent = NewAgent(mock_backend)
        prompt = agent.get_system_prompt()
        assert "specialized agent" in prompt.lower()
    
    @pytest.mark.asyncio
    async def test_process(self, mock_backend):
        agent = NewAgent(mock_backend)
        success, response, error = await agent.process("test input")
        assert success is True
```

## 🔧 Adding New Backends

### 1. Create Backend Class

```python
# explainstack/backends/new_backend.py
from .base_backend import BaseBackend
import requests  # or appropriate library

class NewBackend(BaseBackend):
    """New AI backend implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = "New Backend"
        self.api_key = config.get("api_key", "")
        self.model = config.get("model", "default-model")
        self.temperature = config.get("temperature", 0.3)
        self.max_tokens = config.get("max_tokens", 1000)
    
    async def generate_response(self, system_prompt: str, user_prompt: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Generate response from the new AI model."""
        try:
            # Prepare request
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            # Make API call
            response = requests.post(
                "https://api.new-backend.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return True, content, None
            else:
                return False, None, f"API Error: {response.status_code}"
                
        except Exception as e:
            return False, None, f"Error: {str(e)}"
```

### 2. Register Backend

```python
# explainstack/backends/__init__.py
from .new_backend import NewBackend

__all__ = [
    'BaseBackend',
    'OpenAIBackend',
    'ClaudeBackend',
    'GeminiBackend',
    'NewBackend'
]
```

### 3. Add to Factory

```python
# explainstack/backends/backend_factory.py
from .new_backend import NewBackend

class BackendFactory:
    @staticmethod
    def create_backend(backend_type: str, config: Dict[str, Any]):
        if backend_type == "openai":
            return OpenAIBackend(config)
        elif backend_type == "claude":
            return ClaudeBackend(config)
        elif backend_type == "gemini":
            return GeminiBackend(config)
        elif backend_type == "new_backend":
            return NewBackend(config)
        else:
            raise ValueError(f"Unknown backend type: {backend_type}")
```

### 4. Add Tests

```python
# tests/test_new_backend.py
import pytest
from explainstack.backends import NewBackend

class TestNewBackend:
    def test_initialization(self):
        config = {"api_key": "test-key", "model": "test-model"}
        backend = NewBackend(config)
        assert backend.name == "New Backend"
        assert backend.api_key == "test-key"
    
    @pytest.mark.asyncio
    @patch('requests.post')
    async def test_generate_response_success(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        mock_post.return_value = mock_response
        
        config = {"api_key": "test-key", "model": "test-model"}
        backend = NewBackend(config)
        
        success, response, error = await backend.generate_response("system", "user")
        
        assert success is True
        assert response == "Test response"
        assert error is None
```

## 🧪 Testing

### Test Structure

```
tests/
├── conftest.py          # Pytest configuration and fixtures
├── test_agents.py       # Agent tests
├── test_backends.py     # Backend tests
├── test_auth.py         # Authentication tests
├── test_cli.py          # CLI tests
├── test_integrations.py # Integration tests
└── test_analytics.py    # Analytics tests
```

### Running Tests

```bash
# Run all tests
python run_tests.py

# Run specific test file
python run_tests.py test_agents.py

# Run with coverage
pytest --cov=explainstack --cov-report=html

# Run specific test
pytest tests/test_agents.py::TestCodeExpertAgent::test_initialization
```

### Writing Tests

```python
# Example test structure
class TestNewFeature:
    def test_initialization(self, mock_dependency):
        """Test feature initialization."""
        feature = NewFeature(mock_dependency)
        assert feature.name == "Expected Name"
    
    @pytest.mark.asyncio
    async def test_async_method(self, mock_dependency):
        """Test async method."""
        feature = NewFeature(mock_dependency)
        result = await feature.async_method("input")
        assert result == "expected_output"
    
    def test_error_handling(self, mock_dependency):
        """Test error handling."""
        feature = NewFeature(mock_dependency)
        with pytest.raises(ValueError):
            feature.method_with_error("invalid_input")
```

### Test Fixtures

```python
# conftest.py
@pytest.fixture
def sample_data():
    """Sample data for tests."""
    return {
        "user_id": "test-user-123",
        "data": "test data"
    }

@pytest.fixture
def mock_external_api():
    """Mock external API."""
    with patch('external.api.call') as mock:
        mock.return_value = {"status": "success"}
        yield mock
```

## 📝 Code Style

### Python Style Guide

We follow PEP 8 with some modifications:

```python
# Good
def calculate_fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number.
    
    Args:
        n: The position in the Fibonacci sequence
        
    Returns:
        The nth Fibonacci number
    """
    if n <= 1:
        return n
    return calculate_fibonacci(n - 1) + calculate_fibonacci(n - 2)

# Bad
def calcFib(n):
    if n<=1:return n
    return calcFib(n-1)+calcFib(n-2)
```

### Type Hints

```python
from typing import Dict, List, Optional, Tuple, Any

def process_data(
    data: List[Dict[str, Any]], 
    options: Optional[Dict[str, Any]] = None
) -> Tuple[bool, Optional[str], Optional[str]]:
    """Process data with optional configuration."""
    pass
```

### Documentation

```python
class ExampleClass:
    """Example class with proper documentation.
    
    This class demonstrates proper documentation style
    for ExplainStack components.
    
    Attributes:
        name: The name of the instance
        config: Configuration dictionary
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """Initialize the example class.
        
        Args:
            name: The name for this instance
            config: Configuration dictionary
            
        Raises:
            ValueError: If name is empty
        """
        if not name:
            raise ValueError("Name cannot be empty")
        self.name = name
        self.config = config
```

### Import Organization

```python
# Standard library imports
import os
import sys
from typing import Dict, List, Optional

# Third-party imports
import requests
import pytest

# Local imports
from .base_agent import BaseAgent
from ..config import get_config
```

## 🚀 Deployment

### Development Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-key"
export LOG_LEVEL="DEBUG"

# Run development server
python -m explainstack.app
```

### Production Deployment

```bash
# Install production dependencies
pip install -r requirements.txt

# Set production environment
export ENVIRONMENT="production"
export LOG_LEVEL="INFO"
export DATABASE_URL="postgresql://user:pass@host/db"

# Run with production server
gunicorn explainstack.app:app --workers 4 --bind 0.0.0.0:8000
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "-m", "explainstack.app"]
```

```bash
# Build and run
docker build -t explainstack .
docker run -p 8000:8000 -e OPENAI_API_KEY=your-key explainstack
```

## 🤝 Contributing

### Contribution Process

1. **Fork the repository**
2. **Create feature branch**
   ```bash
   git checkout -b feature/new-feature
   ```
3. **Make changes**
4. **Add tests**
5. **Run tests**
   ```bash
   python run_tests.py
   ```
6. **Commit changes**
   ```bash
   git commit -m "feat: add new feature"
   ```
7. **Push to fork**
   ```bash
   git push origin feature/new-feature
   ```
8. **Create pull request**

### Commit Message Format

```
type(scope): description

feat(agents): add new security expert agent
fix(backend): resolve OpenAI API timeout issue
docs(readme): update installation instructions
test(agents): add unit tests for security expert
```

### Pull Request Guidelines

- **Clear description** of changes
- **Reference issues** if applicable
- **Include tests** for new features
- **Update documentation** if needed
- **Follow code style** guidelines

### Code Review Process

1. **Automated checks** must pass
2. **Code review** by maintainers
3. **Testing** in development environment
4. **Documentation** updates if needed
5. **Approval** and merge

## 📚 Additional Resources

### Development Tools

- **IDE**: VS Code, PyCharm, or your preferred editor
- **Linting**: flake8, black, mypy
- **Testing**: pytest, pytest-cov
- **Documentation**: Sphinx, MkDocs

### Useful Commands

```bash
# Format code
black explainstack/

# Lint code
flake8 explainstack/

# Type check
mypy explainstack/

# Run tests
pytest tests/

# Generate coverage report
pytest --cov=explainstack --cov-report=html

# Install development dependencies
pip install -r requirements-dev.txt
```

### Debugging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Add debug prints
print(f"Debug: {variable}")

# Use debugger
import pdb; pdb.set_trace()
```

### Performance Profiling

```python
import cProfile
import pstats

# Profile function
cProfile.run('your_function()', 'profile_output')

# Analyze results
stats = pstats.Stats('profile_output')
stats.sort_stats('cumulative').print_stats(10)
```
