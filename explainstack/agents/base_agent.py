"""Base agent class for ExplainStack multi-agent system."""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
import openai

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all ExplainStack agents."""
    
    def __init__(self, name: str, description: str, config: Dict[str, Any]):
        """Initialize the agent.
        
        Args:
            name: Agent name (e.g., "Code Expert")
            description: Agent description for UI
            config: Configuration dictionary
        """
        self.name = name
        self.description = description
        self.config = config
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
            self.logger.info(f"Processing with {self.name} agent")
            
            system_prompt = self.get_system_prompt()
            user_prompt = self.get_user_prompt(user_input)
            
            response = openai.ChatCompletion.create(
                model=self.config.get("model", "gpt-4"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.config.get("temperature", 0.3),
                max_tokens=self.config.get("max_tokens", 2000),
            )
            
            result = response.choices[0].message["content"]
            self.logger.info(f"{self.name} agent processed successfully")
            return True, result, None
            
        except openai.error.RateLimitError as e:
            error_msg = "Rate limit exceeded. Please try again in a few minutes."
            self.logger.warning(f"Rate limit error in {self.name}: {e}")
            return False, None, error_msg
            
        except openai.error.InvalidRequestError as e:
            error_msg = "Invalid request. Please check your input."
            self.logger.warning(f"Invalid request error in {self.name}: {e}")
            return False, None, error_msg
            
        except openai.error.AuthenticationError as e:
            error_msg = "Authentication error. Please check your OpenAI API key."
            self.logger.error(f"Authentication error in {self.name}: {e}")
            return False, None, error_msg
            
        except openai.error.APIConnectionError as e:
            error_msg = "API connection error. Please check your internet connection."
            self.logger.error(f"API connection error in {self.name}: {e}")
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
