# 🧠 ExplainStack

> An AI-powered assistant that helps you understand, clean, and review OpenStack Python code and patches.

ExplainStack is a developer tool powered by GPT-4. It provides natural language explanations for Python code, Gerrit patches, and helps maintain clean imports following OpenStack's HACKING guidelines.

## ✨ Features

### 🤖 Multi-Agent System with Multiple AI Backends
- **🧠 Code Expert**: Specialized in explaining Python code and OpenStack patterns (OpenAI GPT-4)
- **🔍 Patch Reviewer**: Expert in reviewing Gerrit patches and code changes (Claude Sonnet)
- **🧹 Import Cleaner**: Specialized in organizing imports according to OpenStack standards (OpenAI GPT-3.5-turbo)
- **💬 Commit Writer**: Expert in generating professional commit messages (OpenAI GPT-4)
- **🎯 Auto-Selection**: Automatically suggests the best agent for your request
- **🔄 Agent Switching**: Easy switching between agents during conversation
- **🌐 Multi-Backend**: Supports OpenAI, Claude, and Gemini for optimal performance and cost
- **🔐 Optional Authentication**: Personal accounts with custom configurations and preferences

### 🛠️ Core Capabilities
- 📝 **Code explanation**: Understand what a Python snippet does, line by line.
- 🔍 **Patch analysis**: Get a pre-review of a Gerrit-style diff.
- 🧹 **Clean imports**: Reorder and simplify imports based on OpenStack's standards.
- 💬 **Commit message suggestions**: Generate professional commit messages for your changes.
- 🧠 **Smart routing**: Automatically figures out what you want and routes to the right agent.
- 🛡️ **Robust error handling**: Comprehensive error management with user-friendly messages.
- 📊 **Logging**: Detailed logging for debugging and monitoring.
- ⚙️ **Configurable**: Customizable via environment variables.

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/explainstack.git
cd explainstack
```

### 2. Install dependencies

Create a virtual environment (optional but recommended):

```bash
python3 -m venv venv
source venv/bin/activate
```

Install Python packages:

```bash
make install
```

Create a `.env` file and add your OpenAI API key:

```bash
cp env.example .env
```

Then edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-...
```

### Multi-Backend Configuration

ExplainStack supports multiple AI providers for optimal performance and cost:

```env
# API Keys (at least one required)
OPENAI_API_KEY=sk-your-openai-api-key-here
CLAUDE_API_KEY=sk-ant-your-claude-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here

# Model Configuration by Agent
OPENAI_MODEL=gpt-4                    # Code Expert & Commit Writer
CLAUDE_MODEL=claude-3-sonnet-20240229 # Patch Reviewer
GEMINI_MODEL=gemini-pro               # Optional for any agent

# Global Settings
LOG_LEVEL=INFO                        # Log level (default: INFO)
```

**Backend Assignment:**
- **Code Expert**: OpenAI GPT-4 (best for code explanation)
- **Patch Reviewer**: Claude Sonnet (excellent for code review)
- **Import Cleaner**: OpenAI GPT-3.5-turbo (cost-effective for simple tasks)
- **Commit Writer**: OpenAI GPT-4 (best for professional writing)

### 🔐 Optional Authentication System

ExplainStack supports both anonymous and authenticated usage:

**Anonymous Mode (Default):**
- Use without creating an account
- Global configuration via environment variables
- Perfect for personal development

**Authenticated Mode:**
- Personal API keys and configuration
- Custom agent preferences
- Session history and analytics
- User-specific themes and settings

**Authentication Commands:**
- Type `login` to sign in
- Type `register` to create an account
- Type `profile` to view your settings
- Type `logout` to sign out

### 3. Run the app

```bash
make run
```

The Chainlit interface will launch in your browser.

## 📖 Usage Examples

### 🤖 Multi-Agent System Usage

**Automatic Agent Selection:**
- Send any code → **Code Expert** agent
- Send a diff/patch → **Patch Reviewer** agent  
- Type "clean imports" + code → **Import Cleaner** agent
- Type "commit message" + diff → **Commit Writer** agent

**Manual Agent Selection:**
- Type `1` for Code Expert
- Type `2` for Patch Reviewer
- Type `3` for Import Cleaner  
- Type `4` for Commit Writer
- Type `auto` for automatic selection

### Code Explanation (Code Expert Agent)
```
def calculate_volume(radius, height):
    return 3.14159 * radius ** 2 * height
```

### Patch Analysis (Patch Reviewer Agent)
```
diff --git a/nova/compute/manager.py b/nova/compute/manager.py
index 1234567..abcdefg 100644
--- a/nova/compute/manager.py
+++ b/nova/compute/manager.py
@@ -100,6 +100,7 @@ class ComputeManager(object):
     def __init__(self):
         self.host = CONF.host
         self.service_name = 'nova-compute'
+        self.metrics = {}
```

### Clean Imports (Import Cleaner Agent)
```
clean imports
import os
import sys
from nova import config
import nova.compute.manager
```

### Commit Message Suggestion (Commit Writer Agent)
```
commit message
diff --git a/nova/api/controllers/volumes.py b/nova/api/controllers/volumes.py
+def create_volume(self, req, body):
+    """Create a new volume."""
+    return self.volume_api.create(req.context, **body['volume'])
```

## 🛠 Makefile Commands

| Command      | Description                     |
|--------------|---------------------------------|
| `make install` | Install dependencies          |
| `make run`     | Start the Chainlit app        |
| `make lint`    | Run flake8 linter             |
| `make format`  | Format code with Black        |

## 📁 Project Structure

```
explainstack/
│
├── app.py              # Main Chainlit app
├── prompts.py          # GPT prompt templates
├── __init__.py
├── ...
├── Makefile
└── todo.md
```

## 📌 TODO

- [x] Multi-agent system with specialized agents
- [x] Automatic agent selection and routing
- [x] Agent selection UI with Chainlit
- [x] Multi-backend support (OpenAI, Claude, Gemini)
- [x] Optional authentication system with SQLite
- [x] User preferences and personal configurations
- [x] Detect user intent (code / diff / cleanup / commit message)
- [x] Clean and restructure imports with HACKING rules
- [x] Suggest commit messages for patches
- [ ] Support `.py` or `.diff` file uploads
- [ ] Add Gerrit integration via API or URL parsing
- [ ] Add Security Expert agent for vulnerability analysis
- [ ] Add Performance Expert agent for optimization suggestions
- [ ] Add OAuth integration (Google, GitHub)
- [ ] Add user analytics and usage tracking

## 💡 Future Ideas

- CLI version (`explainstack analyze file.py`)
- Auto-review comments for patches
- Integration with code editors (VSCode, Neovim)
- Scoring patch quality / style


---

## 📜 License

MIT License – feel free to use, adapt, and improve!