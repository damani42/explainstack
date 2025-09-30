"""Gemini backend for ExplainStack multi-agent system."""

import google.generativeai as genai
from typing import Dict, Any, Optional, Tuple
from .base_backend import BaseBackend


class GeminiBackend(BaseBackend):
    """Gemini backend implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Gemini backend.
        
        Args:
            config: Gemini configuration
        """
        super().__init__("Gemini", config)
        self._setup_gemini()
    
    def _validate_config(self):
        """Validate Gemini configuration."""
        required_keys = ["api_key", "model"]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Gemini config missing required key: {key}")
    
    def _setup_gemini(self):
        """Setup Gemini API."""
        genai.configure(api_key=self.config["api_key"])
        self.model = genai.GenerativeModel(self.config["model"])
        self.logger.info(f"Gemini backend initialized with model: {self.config['model']}")
    
    async def generate_response(
        self, 
        system_prompt: str, 
        user_prompt: str,
        **kwargs
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Generate response using Gemini.
        
        Args:
            system_prompt: System prompt for the AI
            user_prompt: User prompt for the AI
            **kwargs: Additional parameters
            
        Returns:
            Tuple of (success, response, error_message)
        """
        try:
            self.logger.info("Generating response with Gemini")
            
            # Merge config with kwargs
            generation_config = {
                "temperature": self.config.get("temperature", 0.3),
                "max_output_tokens": self.config.get("max_tokens", 2000),
                **kwargs
            }
            
            # Gemini uses a single prompt with system context
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(**generation_config)
            )
            
            result = response.text
            self.logger.info("Gemini response generated successfully")
            return True, result, None
            
        except Exception as e:
            error_msg = f"Gemini error: {str(e)}"
            self.logger.error(f"Gemini error: {e}")
            return False, None, error_msg
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Gemini model information.
        
        Returns:
            Dictionary with model information
        """
        model = self.config["model"]
        
        # Model pricing (per 1M tokens, approximate)
        pricing = {
            "gemini-pro": {"input": 0.5, "output": 1.5},
            "gemini-pro-vision": {"input": 0.5, "output": 1.5},
            "gemini-1.5-pro": {"input": 1.25, "output": 5.0},
            "gemini-1.5-flash": {"input": 0.075, "output": 0.3}
        }
        
        return {
            "name": model,
            "provider": "Google",
            "pricing": pricing.get(model, {"input": 0.5, "output": 1.5}),
            "max_tokens": self.config.get("max_tokens", 2000),
            "temperature": self.config.get("temperature", 0.3)
        }
    
    def get_cost_estimate(self, tokens: int) -> float:
        """Get estimated cost for Gemini token usage.
        
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
        
        # Gemini pricing is per 1M tokens
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost
