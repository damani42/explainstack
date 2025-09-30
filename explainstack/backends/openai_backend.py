"""OpenAI backend for ExplainStack multi-agent system."""

import openai
from typing import Dict, Any, Optional, Tuple
from .base_backend import BaseBackend


class OpenAIBackend(BaseBackend):
    """OpenAI backend implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize OpenAI backend.
        
        Args:
            config: OpenAI configuration
        """
        super().__init__("OpenAI", config)
        self._setup_openai()
    
    def _validate_config(self):
        """Validate OpenAI configuration."""
        required_keys = ["api_key", "model"]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"OpenAI config missing required key: {key}")
    
    def _setup_openai(self):
        """Setup OpenAI API."""
        openai.api_key = self.config["api_key"]
        self.logger.info(f"OpenAI backend initialized with model: {self.config['model']}")
    
    async def generate_response(
        self, 
        system_prompt: str, 
        user_prompt: str,
        **kwargs
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Generate response using OpenAI.
        
        Args:
            system_prompt: System prompt for the AI
            user_prompt: User prompt for the AI
            **kwargs: Additional parameters
            
        Returns:
            Tuple of (success, response, error_message)
        """
        try:
            self.logger.info("Generating response with OpenAI")
            
            # Merge config with kwargs
            request_config = {
                "model": self.config["model"],
                "temperature": self.config.get("temperature", 0.3),
                "max_tokens": self.config.get("max_tokens", 2000),
                **kwargs
            }
            
            response = openai.ChatCompletion.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                **request_config
            )
            
            result = response.choices[0].message["content"]
            self.logger.info("OpenAI response generated successfully")
            return True, result, None
            
        except openai.error.RateLimitError as e:
            error_msg = "OpenAI rate limit exceeded. Please try again in a few minutes."
            self.logger.warning(f"OpenAI rate limit error: {e}")
            return False, None, error_msg
            
        except openai.error.InvalidRequestError as e:
            error_msg = "OpenAI invalid request. Please check your input."
            self.logger.warning(f"OpenAI invalid request error: {e}")
            return False, None, error_msg
            
        except openai.error.AuthenticationError as e:
            error_msg = "OpenAI authentication error. Please check your API key."
            self.logger.error(f"OpenAI authentication error: {e}")
            return False, None, error_msg
            
        except openai.error.APIConnectionError as e:
            error_msg = "OpenAI API connection error. Please check your internet connection."
            self.logger.error(f"OpenAI API connection error: {e}")
            return False, None, error_msg
            
        except Exception as e:
            error_msg = f"OpenAI unexpected error: {str(e)}"
            self.logger.error(f"OpenAI unexpected error: {e}")
            return False, None, error_msg
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get OpenAI model information.
        
        Returns:
            Dictionary with model information
        """
        model = self.config["model"]
        
        # Model pricing (per 1K tokens, approximate)
        pricing = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.001, "output": 0.002},
            "gpt-3.5-turbo-16k": {"input": 0.003, "output": 0.004}
        }
        
        return {
            "name": model,
            "provider": "OpenAI",
            "pricing": pricing.get(model, {"input": 0.001, "output": 0.002}),
            "max_tokens": self.config.get("max_tokens", 2000),
            "temperature": self.config.get("temperature", 0.3)
        }
    
    def get_cost_estimate(self, tokens: int) -> float:
        """Get estimated cost for OpenAI token usage.
        
        Args:
            tokens: Number of tokens
            
        Returns:
            Estimated cost in USD
        """
        model_info = self.get_model_info()
        pricing = model_info["pricing"]
        
        # Assume 70% input, 30% output tokens
        input_tokens = int(tokens * 0.7)
        output_tokens = int(tokens * 0.3)
        
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        
        return input_cost + output_cost
