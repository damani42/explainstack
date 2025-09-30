# 🧠 ExplainStack

> An AI-powered assistant that helps you understand, clean, and review OpenStack Python code and patches.

ExplainStack is a developer tool powered by GPT-4. It provides natural language explanations for Python code, Gerrit patches, and helps maintain clean imports following OpenStack's HACKING guidelines.

## ✨ Features

- 📝 **Code explanation**: Understand what a Python snippet does, line by line.
- 🔍 **Patch analysis**: Get a pre-review of a Gerrit-style diff.
- 🧹 **Clean imports**: Reorder and simplify imports based on OpenStack's standards.
- 🧠 **Intent detection**: Automatically figures out what you want (code, patch, or cleanup).
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

- [x] Detect user intent (code / diff / cleanup)
- [x] Clean and restructure imports with HACKING rules
- [ ] Suggest commit messages for patches
- [ ] Support `.py` or `.diff` file uploads
- [ ] Add Gerrit integration via API or URL parsing

## 💡 Future Ideas

- CLI version (`explainstack analyze file.py`)
- Auto-review comments for patches
- Integration with code editors (VSCode, Neovim)
- Scoring patch quality / style


---

## 📜 License

MIT License – feel free to use, adapt, and improve!