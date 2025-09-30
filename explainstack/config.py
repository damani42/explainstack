"""Configuration for ExplainStack."""

import os
from typing import Dict, Any

# Default configuration
DEFAULT_CONFIG: Dict[str, Any] = {
    "backends": {
        "code_expert": {
            "type": "openai",
            "config": {
                "api_key": "",
                "model": "gpt-4",
                "temperature": 0.3,
                "max_tokens": 2000
            }
        },
        "patch_reviewer": {
            "type": "claude",
            "config": {
                "api_key": "",
                "model": "claude-3-sonnet-20240229",
                "temperature": 0.2,
                "max_tokens": 3000
            }
        },
        "import_cleaner": {
            "type": "openai",
            "config": {
                "api_key": "",
                "model": "gpt-3.5-turbo",
                "temperature": 0.1,
                "max_tokens": 1000
            }
        },
        "commit_writer": {
            "type": "openai",
            "config": {
                "api_key": "",
                "model": "gpt-4",
                "temperature": 0.3,
                "max_tokens": 1500
            }
        }
    },
    "validation": {
        "max_input_length": 10000,
        "min_input_length": 1,
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    }
}

def get_config() -> Dict[str, Any]:
    """Get configuration with environment variables."""
    config = DEFAULT_CONFIG.copy()
    
    # Override with environment variables if available
    # OpenAI configuration
    if os.getenv("OPENAI_API_KEY"):
        config["backends"]["code_expert"]["config"]["api_key"] = os.getenv("OPENAI_API_KEY")
        config["backends"]["import_cleaner"]["config"]["api_key"] = os.getenv("OPENAI_API_KEY")
        config["backends"]["commit_writer"]["config"]["api_key"] = os.getenv("OPENAI_API_KEY")
    
    if os.getenv("OPENAI_MODEL"):
        config["backends"]["code_expert"]["config"]["model"] = os.getenv("OPENAI_MODEL")
        config["backends"]["import_cleaner"]["config"]["model"] = os.getenv("OPENAI_MODEL")
        config["backends"]["commit_writer"]["config"]["model"] = os.getenv("OPENAI_MODEL")
    
    # Claude configuration
    if os.getenv("CLAUDE_API_KEY"):
        config["backends"]["patch_reviewer"]["config"]["api_key"] = os.getenv("CLAUDE_API_KEY")
    
    if os.getenv("CLAUDE_MODEL"):
        config["backends"]["patch_reviewer"]["config"]["model"] = os.getenv("CLAUDE_MODEL")
    
    # Gemini configuration
    if os.getenv("GEMINI_API_KEY"):
        # You can add Gemini to any agent by changing the type
        pass
    
    if os.getenv("GEMINI_MODEL"):
        # You can add Gemini to any agent by changing the type
        pass
    
    # Global settings
    if os.getenv("LOG_LEVEL"):
        config["logging"]["level"] = os.getenv("LOG_LEVEL")
    
    return config
