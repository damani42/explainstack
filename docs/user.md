# 👤 User Guide

Complete user manual for ExplainStack.

## 📋 Table of Contents

- [Installation & Setup](#installation--setup)
- [Basic Usage](#basic-usage)
- [CLI Commands](#cli-commands)
- [Web Interface](#web-interface)
- [Configuration](#configuration)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8 or higher
- Internet connection for AI API calls
- At least one AI API key (OpenAI, Claude, or Gemini)

### Quick Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-username/explainstack.git
cd explainstack
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp env.example .env
# Edit .env with your API keys
```

4. **Run the application**
```bash
python -m explainstack.app
```

### Detailed Installation

#### Option 1: Using pip (Recommended)

```bash
# Install from PyPI (when available)
pip install explainstack

# Or install from source
pip install git+https://github.com/your-username/explainstack.git
```

#### Option 2: From Source

```bash
# Clone repository
git clone https://github.com/your-username/explainstack.git
cd explainstack

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### API Key Configuration

#### OpenAI API Key
```bash
# Get your API key from https://platform.openai.com/api-keys
export OPENAI_API_KEY="sk-your-openai-key-here"
```

#### Claude API Key
```bash
# Get your API key from https://console.anthropic.com/
export CLAUDE_API_KEY="sk-ant-your-claude-key-here"
```

#### Gemini API Key
```bash
# Get your API key from https://makersuite.google.com/app/apikey
export GEMINI_API_KEY="your-gemini-key-here"
```

#### Environment File (.env)
```bash
# Create .env file
OPENAI_API_KEY=sk-your-openai-key-here
CLAUDE_API_KEY=sk-ant-your-claude-key-here
GEMINI_API_KEY=your-gemini-key-here

# Optional configuration
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///explainstack.db
```

## 🎯 Basic Usage

### Web Interface

1. **Start the web interface**
```bash
python -m explainstack.app
```

2. **Open your browser**
Navigate to `http://localhost:8000`

3. **Start using ExplainStack**
- Type your Python code or paste a diff
- Ask questions about OpenStack development
- Upload files for analysis

### CLI Interface

1. **Install CLI tool**
```bash
# Install globally
sudo python3 setup_cli.py

# Or install to user directory
python3 setup_cli.py --user
```

2. **Use CLI commands**
```bash
# Analyze Python code
explainstack analyze file.py

# Security analysis
explainstack security file.py

# Review patch
explainstack review patch.diff
```

## 🖥️ CLI Commands

### Basic Commands

#### Analyze Code
```bash
# Analyze Python code
explainstack analyze file.py

# Use specific agent
explainstack analyze file.py --agent code_expert

# Save output to file
explainstack analyze file.py --output analysis.md
```

#### Security Analysis
```bash
# Security analysis
explainstack security file.py

# Verbose output
explainstack security file.py --verbose

# Save security report
explainstack security file.py --output security_report.md
```

#### Performance Analysis
```bash
# Performance analysis
explainstack performance file.py

# Use specific agent
explainstack performance file.py --agent performance_expert
```

#### Patch Review
```bash
# Review patch
explainstack review patch.diff

# Review with specific agent
explainstack review patch.diff --agent patch_reviewer
```

#### Import Cleaning
```bash
# Clean imports
explainstack clean file.py

# Save cleaned file
explainstack clean file.py --output cleaned_file.py
```

#### Commit Message Generation
```bash
# Generate commit message
explainstack commit file.py

# Generate from diff
explainstack commit patch.diff
```

### Advanced CLI Usage

#### Global Options
```bash
# Verbose output
explainstack analyze file.py --verbose

# Specify agent
explainstack analyze file.py --agent security_expert

# Save output
explainstack analyze file.py --output result.md

# Help
explainstack --help
explainstack analyze --help
```

#### Batch Processing
```bash
# Process multiple files
for file in *.py; do
    explainstack analyze "$file" --output "${file%.py}_analysis.md"
done
```

#### Integration with Git
```bash
# Analyze staged changes
git diff --cached | explainstack review

# Generate commit message for staged changes
git diff --cached | explainstack commit
```

## 🌐 Web Interface

### Getting Started

1. **Access the interface**
   - Open `http://localhost:8000` in your browser
   - No installation required for the web interface

2. **Basic interaction**
   - Type your code or question in the chat
   - Upload files using the file upload feature
   - Paste Gerrit URLs for automatic analysis

### Features

#### Agent Selection
- **Automatic**: ExplainStack automatically selects the best agent
- **Manual**: Choose specific agents for your needs
- **Switching**: Switch between agents during conversation

#### File Upload
- **Supported formats**: .py, .diff, .patch, .txt, .md
- **Size limit**: 10MB per file
- **Batch processing**: Upload multiple files

#### Gerrit Integration
- **URL detection**: Automatically detects Gerrit URLs
- **Change analysis**: Fetches and analyzes Gerrit changes
- **Diff processing**: Processes diffs for analysis

### Account Features

#### Registration
```bash
# In the web interface, type:
register

# Follow the prompts to create an account
```

#### Login
```bash
# In the web interface, type:
login

# Enter your credentials
```

#### API Key Configuration
```bash
# In the web interface, type:
api

# Configure your personal API keys
```

#### Analytics Dashboard
```bash
# In the web interface, type:
analytics

# View your usage statistics
```

## ⚙️ Configuration

### Environment Variables

#### Required Variables
```bash
# At least one API key is required
OPENAI_API_KEY=sk-your-openai-key-here
CLAUDE_API_KEY=sk-ant-your-claude-key-here
GEMINI_API_KEY=your-gemini-key-here
```

#### Optional Variables
```bash
# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Database
DATABASE_URL=sqlite:///explainstack.db

# OAuth (optional)
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GITHUB_OAUTH_CLIENT_ID=your-github-client-id
```

### Agent Configuration

#### Default Agent Assignment
```bash
# Code Expert (OpenAI GPT-4)
OPENAI_MODEL=gpt-4

# Patch Reviewer (Claude Sonnet)
CLAUDE_MODEL=claude-3-sonnet-20240229

# Security Expert (Claude Sonnet)
CLAUDE_MODEL=claude-3-sonnet-20240229

# Performance Expert (OpenAI GPT-4)
OPENAI_MODEL=gpt-4
```

#### Custom Configuration
```python
# config.py
DEFAULT_CONFIG = {
    "backends": {
        "code_expert": {
            "type": "openai",
            "config": {
                "model": "gpt-4",
                "temperature": 0.3,
                "max_tokens": 2000
            }
        }
    }
}
```

### Personal API Keys

#### Setting Personal Keys
```bash
# In the web interface
api

# Set OpenAI key
set openai sk-your-personal-key

# Set Claude key
set claude sk-ant-your-personal-key

# Test all keys
test keys

# Clear all keys
clear keys
```

## 📚 Examples

### Code Analysis Examples

#### Basic Python Code
```python
# Input
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# ExplainStack will explain:
# - Function purpose
# - Algorithm complexity
# - Optimization suggestions
```

#### OpenStack Code
```python
# Input
class ComputeManager(manager.Manager):
    def __init__(self, *args, **kwargs):
        super(ComputeManager, self).__init__(*args, **kwargs)
        self.driver = driver.load_compute_driver()
    
    def create_instance(self, context, instance):
        # Implementation
        pass

# ExplainStack will explain:
# - OpenStack patterns
# - Manager inheritance
# - Instance creation flow
```

### Security Analysis Examples

#### Input Validation
```python
# Input
user_input = request.GET.get('id')
query = f"SELECT * FROM users WHERE id = {user_input}"

# ExplainStack will identify:
# - SQL injection vulnerability
# - Input validation issues
# - Secure coding practices
```

#### Authentication
```python
# Input
def authenticate_user(username, password):
    user = User.objects.get(username=username)
    if user.password == password:
        return user
    return None

# ExplainStack will identify:
# - Password hashing issues
# - Authentication vulnerabilities
# - Security best practices
```

### Performance Analysis Examples

#### Inefficient Loops
```python
# Input
def process_data(data):
    result = []
    for item in data:
        processed = expensive_operation(item)
        result.append(processed)
    return result

# ExplainStack will suggest:
# - List comprehensions
# - Generator expressions
# - Caching strategies
```

#### Database Queries
```python
# Input
def get_user_posts(user_id):
    posts = []
    for post_id in Post.objects.filter(user_id=user_id):
        posts.append(post_id)
    return posts

# ExplainStack will suggest:
# - Query optimization
# - Database indexing
# - Caching strategies
```

### Patch Review Examples

#### Gerrit Patch
```diff
# Input
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

# ExplainStack will review:
# - Code changes
# - OpenStack conventions
# - Potential issues
# - Improvement suggestions
```

### Import Cleaning Examples

#### Messy Imports
```python
# Input
import os, sys, json
from django.conf import settings
import requests
from .models import User
import logging
from django.contrib.auth import authenticate

# ExplainStack will organize:
# - Standard library imports
# - Third-party imports
# - Local imports
# - Alphabetical ordering
```

### Commit Message Examples

#### Code Changes
```diff
# Input
diff --git a/nova/compute/manager.py b/nova/compute/manager.py
+    def create_instance(self, context, instance):
+        """Create a new instance."""
+        return self.driver.create_instance(context, instance)

# ExplainStack will generate:
# feat(compute): Add create_instance method to ComputeManager
# 
# Implements instance creation functionality following
# OpenStack conventions. Includes proper error handling
# and documentation.
# 
# Fixes: #12345
```

## 🔧 Troubleshooting

### Common Issues

#### API Key Issues
```bash
# Error: No API key configured
# Solution: Set at least one API key
export OPENAI_API_KEY="sk-your-key-here"
```

#### Import Errors
```bash
# Error: ModuleNotFoundError
# Solution: Install dependencies
pip install -r requirements.txt
```

#### Permission Errors
```bash
# Error: Permission denied
# Solution: Use user installation
python3 setup_cli.py --user
```

#### Network Issues
```bash
# Error: Connection timeout
# Solution: Check internet connection and API key validity
```

### Debug Mode

#### Enable Debug Logging
```bash
export LOG_LEVEL=DEBUG
python -m explainstack.app
```

#### CLI Debug
```bash
explainstack analyze file.py --verbose
```

#### Check Configuration
```bash
# Test API keys
explainstack analyze file.py --agent code_expert

# Check agent selection
explainstack analyze "explain this code"
```

### Performance Issues

#### Slow Responses
```bash
# Use faster models
export OPENAI_MODEL=gpt-3.5-turbo

# Reduce max tokens
export OPENAI_MAX_TOKENS=1000
```

#### Memory Issues
```bash
# Reduce batch size
export BATCH_SIZE=1

# Clear cache
rm -rf .cache/
```

### Getting Help

#### Documentation
- Check this user guide
- Read the [API documentation](api.md)
- Review [developer guide](developer.md)

#### Community Support
- GitHub Issues: Report bugs and request features
- GitHub Discussions: Ask questions and share ideas
- Pull Requests: Contribute improvements

#### Professional Support
- Enterprise support available
- Custom integrations
- Training and consulting

### Error Messages

#### Common Error Messages

```bash
# API Key Error
❌ Error: No API key configured
Solution: Set OPENAI_API_KEY, CLAUDE_API_KEY, or GEMINI_API_KEY

# File Not Found
❌ Error: File not found: file.py
Solution: Check file path and permissions

# Agent Error
❌ Error: Agent 'unknown' not found
Solution: Use valid agent name (code_expert, security_expert, etc.)

# Backend Error
❌ Error: Backend 'unknown' not found
Solution: Use valid backend type (openai, claude, gemini)
```

#### Debug Information

```bash
# Get system information
explainstack --version
explainstack --help

# Check configuration
python -c "from explainstack.config import get_config; print(get_config())"

# Test API connectivity
python -c "from explainstack.backends import OpenAIBackend; print('API test')"
```
