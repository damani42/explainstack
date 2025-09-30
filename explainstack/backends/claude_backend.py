"""Claude backend for ExplainStack multi-agent system."""

import anthropic
from typing import Dict, Any, Optional, Tuple
from .base_backend import BaseBackend


class ClaudeBackend(BaseBackend):
    """Claude backend implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Claude backend.
        
        Args:
            config: Claude configuration
        """
        super().__init__("Claude", config)
        self._setup_claude()
    
    def _validate_config(self):
        """Validate Claude configuration."""
        required_keys = ["api_key", "model"]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Claude config missing required key: {key}")
    
    def _setup_claude(self):
        """Setup Claude API."""
        self.client = anthropic.Anthropic(api_key=self.config["api_key"])
        self.logger.info(f"Claude backend initialized with model: {self.config['model']}")
    
    async def generate_response(
        self, 
        system_prompt: str, 
        user_prompt: str,
        **kwargs
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Generate response using Claude.
        
        Args:
            system_prompt: System prompt for the AI
            user_prompt: User prompt for the AI
            **kwargs: Additional parameters
            
        Returns:
            Tuple of (success, response, error_message)
        """
        try:
            self.logger.info("Generating response with Claude")
            
            # Merge config with kwargs
            request_config = {
                "model": self.config["model"],
                "temperature": self.config.get("temperature", 0.3),
                "max_tokens": self.config.get("max_tokens", 2000),
                **kwargs
            }
            
            # Claude uses a single message with system prompt
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            response = self.client.messages.create(
                messages=[{"role": "user", "content": full_prompt}],
                **request_config
            )
            
            result = response.content[0].text
            self.logger.info("Claude response generated successfully")
            return True, result, None
            
        except anthropic.RateLimitError as e:
            error_msg = "Claude rate limit exceeded. Please try again in a few minutes."
            self.logger.warning(f"Claude rate limit error: {e}")
            return False, None, error_msg
            
        except anthropic.InvalidRequestError as e:
            error_msg = "Claude invalid request. Please check your input."
            self.logger.warning(f"Claude invalid request error: {e}")
            return False, None, error_msg
            
        except anthropic.AuthenticationError as e:
            error_msg = "Claude authentication error. Please check your API key."
            self.logger.error(f"Claude authentication error: {e}")
            return False, None, error_msg
            
        except anthropic.APIConnectionError as e:
            error_msg = "Claude API connection error. Please check your internet connection."
            self.logger.error(f"Claude API connection error: {e}")
            return False, None, error_msg
            
        except Exception as e:
            error_msg = f"Claude unexpected error: {str(e)}"
            self.logger.error(f"Claude unexpected error: {e}")
            return False, None, error_msg
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Claude model information.
        
        Returns:
            Dictionary with model information
        """
        model = self.config["model"]
        
        # Model pricing (per 1K tokens, approximate)
        pricing = {
            "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
            "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125}
        }
        
        return {
            "name": model,
            "provider": "Anthropic",
            "pricing": pricing.get(model, {"input": 0.003, "output": 0.015}),
            "max_tokens": self.config.get("max_tokens", 2000),
            "temperature": self.config.get("temperature", 0.3)
        }
    
    def get_cost_estimate(self, tokens: int) -> float:
        """Get estimated cost for Claude token usage.
        
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
