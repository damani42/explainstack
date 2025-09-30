"""User service for ExplainStack."""

import logging
from typing import Optional, Dict, Any
from ..database import User, UserPreferences
from ..auth import AuthService

logger = logging.getLogger(__name__)


class UserService:
    """User service for ExplainStack."""
    
    def __init__(self, auth_service: AuthService):
        """Initialize user service.
        
        Args:
            auth_service: Authentication service instance
        """
        self.auth_service = auth_service
        self.logger = logging.getLogger(__name__)
    
    def get_user_profile(self, user: User) -> Dict[str, Any]:
        """Get user profile information.
        
        Args:
            user: User instance
            
        Returns:
            User profile dictionary
        """
        try:
            preferences = self.auth_service.get_user_preferences(user.user_id)
            
            return {
                "user_id": user.user_id,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
                "is_active": user.is_active,
                "preferences": preferences.to_dict() if preferences else {},
                "stats": self._get_user_stats(user)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get user profile: {e}")
            return {
                "user_id": user.user_id,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
                "is_active": user.is_active,
                "preferences": {},
                "stats": {}
            }
    
    def update_user_preferences(self, user: User, preferences_data: Dict[str, Any]) -> bool:
        """Update user preferences.
        
        Args:
            user: User instance
            preferences_data: New preferences data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current preferences
            current_preferences = self.auth_service.get_user_preferences(user.user_id)
            if not current_preferences:
                # Create new preferences
                current_preferences = UserPreferences.create_default(user.user_id)
            
            # Update preferences
            for key, value in preferences_data.items():
                current_preferences.set_preference(key, value)
            
            # Save to database
            success, message = self.auth_service.update_user_preferences(
                user.user_id, current_preferences
            )
            
            if success:
                self.logger.info(f"Preferences updated for user: {user.user_id}")
                return True
            else:
                self.logger.error(f"Failed to update preferences: {message}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to update user preferences: {e}")
            return False
    
    def get_user_api_keys(self, user: User) -> Dict[str, str]:
        """Get user API keys.
        
        Args:
            user: User instance
            
        Returns:
            Dictionary of API keys
        """
        try:
            preferences = self.auth_service.get_user_preferences(user.user_id)
            if not preferences:
                return {}
            
            return {
                "openai_api_key": preferences.get_preference("openai_api_key", ""),
                "claude_api_key": preferences.get_preference("claude_api_key", ""),
                "gemini_api_key": preferences.get_preference("gemini_api_key", "")
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get user API keys: {e}")
            return {}
    
    def update_user_api_keys(self, user: User, api_keys: Dict[str, str]) -> bool:
        """Update user API keys.
        
        Args:
            user: User instance
            api_keys: Dictionary of API keys
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current preferences
            current_preferences = self.auth_service.get_user_preferences(user.user_id)
            if not current_preferences:
                current_preferences = UserPreferences.create_default(user.user_id)
            
            # Update API keys
            for key, value in api_keys.items():
                if key in ["openai_api_key", "claude_api_key", "gemini_api_key"]:
                    current_preferences.set_preference(key, value)
            
            # Save to database
            success, message = self.auth_service.update_user_preferences(
                user.user_id, current_preferences
            )
            
            if success:
                self.logger.info(f"API keys updated for user: {user.user_id}")
                return True
            else:
                self.logger.error(f"Failed to update API keys: {message}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to update user API keys: {e}")
            return False
    
    def _get_user_stats(self, user: User) -> Dict[str, Any]:
        """Get user statistics.
        
        Args:
            user: User instance
            
        Returns:
            User statistics dictionary
        """
        try:
            # This would be implemented with actual usage tracking
            # For now, return placeholder stats
            return {
                "total_sessions": 0,
                "total_requests": 0,
                "favorite_agent": "auto",
                "last_active": user.created_at.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get user stats: {e}")
            return {}
