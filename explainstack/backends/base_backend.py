"""Base backend interface for ExplainStack multi-agent system."""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class BaseBackend(ABC):
    """Base class for all AI backend providers."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """Initialize the backend.
        
        Args:
            name: Backend name (e.g., "OpenAI", "Claude", "Gemini")
            config: Backend configuration
        """
        self.name = name
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self):
        """Validate backend configuration."""
        pass
    
    @abstractmethod
    async def generate_response(
        self, 
        system_prompt: str, 
        user_prompt: str,
        **kwargs
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Generate response using the backend.
        
        Args:
            system_prompt: System prompt for the AI
            user_prompt: User prompt for the AI
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            Tuple of (success, response, error_message)
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the backend model.
        
        Returns:
            Dictionary with model information
        """
        pass
    
    def get_cost_estimate(self, tokens: int) -> float:
        """Get estimated cost for token usage.
        
        Args:
            tokens: Number of tokens
            
        Returns:
            Estimated cost in USD
        """
        # Default implementation - should be overridden
        return 0.0
    
    def get_info(self) -> Dict[str, Any]:
        """Get backend information.
        
        Returns:
            Dictionary with backend information
        """
        return {
            "name": self.name,
            "model": self.get_model_info(),
            "config": self.config
        }
