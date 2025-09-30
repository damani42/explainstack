"""Configuration for ExplainStack."""

import os
from typing import Dict, Any

# Default configuration
DEFAULT_CONFIG: Dict[str, Any] = {
    "openai": {
        "model": "gpt-4",
        "temperature": 0.3,
        "max_tokens": 2000,
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
    if os.getenv("OPENAI_MODEL"):
        config["openai"]["model"] = os.getenv("OPENAI_MODEL")
    
    if os.getenv("OPENAI_TEMPERATURE"):
        try:
            config["openai"]["temperature"] = float(os.getenv("OPENAI_TEMPERATURE"))
        except ValueError:
            pass  # Keep default value
    
    if os.getenv("OPENAI_MAX_TOKENS"):
        try:
            config["openai"]["max_tokens"] = int(os.getenv("OPENAI_MAX_TOKENS"))
        except ValueError:
            pass  # Keep default value
    
    if os.getenv("LOG_LEVEL"):
        config["logging"]["level"] = os.getenv("LOG_LEVEL")
    
    return config
