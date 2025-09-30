"""Authentication middleware for ExplainStack."""

import logging
from typing import Optional, Dict, Any
from .auth_service import AuthService
from ..database import User, UserPreferences

logger = logging.getLogger(__name__)


class AuthMiddleware:
    """Authentication middleware for Chainlit."""
    
    def __init__(self, auth_service: AuthService):
        """Initialize authentication middleware.
        
        Args:
            auth_service: Authentication service instance
        """
        self.auth_service = auth_service
        self.logger = logging.getLogger(__name__)
    
    def get_current_user(self, session_id: Optional[str] = None) -> Optional[User]:
        """Get current user from session.
        
        Args:
            session_id: Session ID (optional)
            
        Returns:
            User instance or None if not authenticated
        """
        if not session_id:
            return None
        
        try:
            return self.auth_service.get_user_from_session(session_id)
        except Exception as e:
            self.logger.error(f"Failed to get current user: {e}")
            return None
    
    def get_user_config(self, user: User) -> Dict[str, Any]:
        """Get user-specific configuration.
        
        Args:
            user: User instance
            
        Returns:
            User configuration dictionary
        """
        try:
            preferences = self.auth_service.get_user_preferences(user.user_id)
            if not preferences:
                # Return default configuration
                return self._get_default_config()
            
            # Build configuration from user preferences
            config = {
                "backends": {
                    "code_expert": {
                        "type": "openai",
                        "config": {
                            "api_key": preferences.get_preference("openai_api_key", ""),
                            "model": preferences.get_preference("preferred_models", {}).get("code_expert", "gpt-4"),
                            "temperature": 0.3,
                            "max_tokens": 2000
                        }
                    },
                    "patch_reviewer": {
                        "type": "claude",
                        "config": {
                            "api_key": preferences.get_preference("claude_api_key", ""),
                            "model": preferences.get_preference("preferred_models", {}).get("patch_reviewer", "claude-3-sonnet-20240229"),
                            "temperature": 0.2,
                            "max_tokens": 3000
                        }
                    },
                    "import_cleaner": {
                        "type": "openai",
                        "config": {
                            "api_key": preferences.get_preference("openai_api_key", ""),
                            "model": preferences.get_preference("preferred_models", {}).get("import_cleaner", "gpt-3.5-turbo"),
                            "temperature": 0.1,
                            "max_tokens": 1000
                        }
                    },
                    "commit_writer": {
                        "type": "openai",
                        "config": {
                            "api_key": preferences.get_preference("openai_api_key", ""),
                            "model": preferences.get_preference("preferred_models", {}).get("commit_writer", "gpt-4"),
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
            
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to get user config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration.
        
        Returns:
            Default configuration dictionary
        """
        from ..config import DEFAULT_CONFIG
        return DEFAULT_CONFIG
    
    def is_authenticated(self, session_id: Optional[str] = None) -> bool:
        """Check if user is authenticated.
        
        Args:
            session_id: Session ID (optional)
            
        Returns:
            True if authenticated, False otherwise
        """
        if not session_id:
            return False
        
        return self.auth_service.is_session_valid(session_id)
    
    def get_user_info(self, user: User) -> Dict[str, Any]:
        """Get user information for UI.
        
        Args:
            user: User instance
            
        Returns:
            User information dictionary
        """
        try:
            preferences = self.auth_service.get_user_preferences(user.user_id)
            
            return {
                "user_id": user.user_id,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
                "preferences": preferences.to_dict() if preferences else {},
                "is_authenticated": True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get user info: {e}")
            return {
                "user_id": user.user_id,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
                "preferences": {},
                "is_authenticated": True
            }
