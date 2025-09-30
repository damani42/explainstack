# 🧠 ExplainStack

> An AI-powered assistant that helps you understand, clean, and review OpenStack Python code and patches.

ExplainStack is a developer tool powered by GPT-4. It provides natural language explanations for Python code, Gerrit patches, and helps maintain clean imports following OpenStack's HACKING guidelines.

## ✨ Features

### 🤖 Multi-Agent System
- **🧠 Code Expert**: Specialized in explaining Python code and OpenStack patterns
- **🔍 Patch Reviewer**: Expert in reviewing Gerrit patches and code changes
- **🧹 Import Cleaner**: Specialized in organizing imports according to OpenStack standards
- **💬 Commit Writer**: Expert in generating professional commit messages
- **🎯 Auto-Selection**: Automatically suggests the best agent for your request
- **🔄 Agent Switching**: Easy switching between agents during conversation

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

### Optional Configuration

You can customize the behavior by setting these environment variables:

```env
# OpenAI Configuration
OPENAI_MODEL=gpt-4                    # Model to use (default: gpt-4)
OPENAI_TEMPERATURE=0.3                # Response creativity (default: 0.3)
OPENAI_MAX_TOKENS=2000                # Max response length (default: 2000)

# Logging
LOG_LEVEL=INFO                        # Log level (default: INFO)
```

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
- [x] Detect user intent (code / diff / cleanup / commit message)
- [x] Clean and restructure imports with HACKING rules
- [x] Suggest commit messages for patches
- [ ] Support `.py` or `.diff` file uploads
- [ ] Add Gerrit integration via API or URL parsing
- [ ] Add Security Expert agent for vulnerability analysis
- [ ] Add Performance Expert agent for optimization suggestions

## 💡 Future Ideas

- CLI version (`explainstack analyze file.py`)
- Auto-review comments for patches
- Integration with code editors (VSCode, Neovim)
- Scoring patch quality / style


---

## 📜 License

MIT License – feel free to use, adapt, and improve!