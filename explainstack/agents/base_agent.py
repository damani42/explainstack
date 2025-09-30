"""Base agent class for ExplainStack multi-agent system."""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
from ..backends import BaseBackend

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all ExplainStack agents."""
    
    def __init__(self, name: str, description: str, backend: BaseBackend):
        """Initialize the agent.
        
        Args:
            name: Agent name (e.g., "Code Expert")
            description: Agent description for UI
            backend: Backend instance for AI processing
        """
        self.name = name
        self.description = description
        self.backend = backend
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        pass
    
    @abstractmethod
    def get_user_prompt(self, user_input: str) -> str:
        """Get the user prompt for this agent."""
        pass
    
    async def process(self, user_input: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Process user input with this agent.
        
        Args:
            user_input: User's input text
            
        Returns:
            Tuple of (success, response, error_message)
        """
        try:
            self.logger.info(f"Processing with {self.name} agent using {self.backend.name} backend")
            
            system_prompt = self.get_system_prompt()
            user_prompt = self.get_user_prompt(user_input)
            
            # Use the configured backend
            success, result, error_msg = await self.backend.generate_response(
                system_prompt, user_prompt
            )
            
            if success:
                self.logger.info(f"{self.name} agent processed successfully")
                return True, result, None
            else:
                self.logger.error(f"{self.name} agent failed: {error_msg}")
                return False, None, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error in {self.name}: {str(e)}"
            self.logger.error(f"Unexpected error in {self.name}: {e}")
            return False, None, error_msg
    
    def get_info(self) -> Dict[str, str]:
        """Get agent information for UI."""
        return {
            "name": self.name,
            "description": self.description,
            "id": self.name.lower().replace(" ", "_")
        }
