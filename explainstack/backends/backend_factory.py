"""Backend factory for ExplainStack multi-agent system."""

import logging
from typing import Dict, Any, Optional
from .base_backend import BaseBackend
from .openai_backend import OpenAIBackend
from .claude_backend import ClaudeBackend
from .gemini_backend import GeminiBackend

logger = logging.getLogger(__name__)


class BackendFactory:
    """Factory for creating AI backend instances."""
    
    _backends = {
        "openai": OpenAIBackend,
        "claude": ClaudeBackend,
        "gemini": GeminiBackend
    }
    
    @classmethod
    def create_backend(cls, backend_type: str, config: Dict[str, Any]) -> BaseBackend:
        """Create a backend instance.
        
        Args:
            backend_type: Type of backend ("openai", "claude", "gemini")
            config: Backend configuration
            
        Returns:
            Backend instance
            
        Raises:
            ValueError: If backend type is not supported
        """
        if backend_type not in cls._backends:
            available = ", ".join(cls._backends.keys())
            raise ValueError(f"Unsupported backend type: {backend_type}. Available: {available}")
        
        backend_class = cls._backends[backend_type]
        logger.info(f"Creating {backend_type} backend")
        
        try:
            return backend_class(config)
        except Exception as e:
            logger.error(f"Failed to create {backend_type} backend: {e}")
            raise
    
    @classmethod
    def get_available_backends(cls) -> list:
        """Get list of available backend types.
        
        Returns:
            List of available backend types
        """
        return list(cls._backends.keys())
    
    @classmethod
    def get_backend_info(cls, backend_type: str) -> Dict[str, str]:
        """Get information about a backend type.
        
        Args:
            backend_type: Type of backend
            
        Returns:
            Dictionary with backend information
        """
        info_map = {
            "openai": {
                "name": "OpenAI",
                "description": "GPT models from OpenAI",
                "models": "GPT-4, GPT-3.5-turbo, GPT-4-turbo"
            },
            "claude": {
                "name": "Claude",
                "description": "Claude models from Anthropic",
                "models": "Claude-3 Opus, Sonnet, Haiku"
            },
            "gemini": {
                "name": "Gemini",
                "description": "Gemini models from Google",
                "models": "Gemini Pro, Gemini 1.5 Pro, Flash"
            }
        }
        
        return info_map.get(backend_type, {
            "name": "Unknown",
            "description": "Unknown backend",
            "models": "Unknown"
        })
