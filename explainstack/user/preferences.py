"""User preferences management for ExplainStack."""

import logging
from typing import Dict, Any, Optional
from ..database import UserPreferences
from ..auth import AuthService

logger = logging.getLogger(__name__)


class UserPreferencesManager:
    """User preferences manager for ExplainStack."""
    
    def __init__(self, auth_service: AuthService):
        """Initialize preferences manager.
        
        Args:
            auth_service: Authentication service instance
        """
        self.auth_service = auth_service
        self.logger = logging.getLogger(__name__)
    
    def get_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """Get user preferences.
        
        Args:
            user_id: User ID
            
        Returns:
            UserPreferences instance or None if not found
        """
        try:
            return self.auth_service.get_user_preferences(user_id)
        except Exception as e:
            self.logger.error(f"Failed to get preferences: {e}")
            return None
    
    def update_preference(self, user_id: str, key: str, value: Any) -> bool:
        """Update a single preference.
        
        Args:
            user_id: User ID
            key: Preference key
            value: Preference value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            preferences = self.auth_service.get_user_preferences(user_id)
            if not preferences:
                preferences = UserPreferences.create_default(user_id)
            
            preferences.set_preference(key, value)
            
            success, message = self.auth_service.update_user_preferences(
                user_id, preferences
            )
            
            if success:
                self.logger.info(f"Preference updated: {key} for user {user_id}")
                return True
            else:
                self.logger.error(f"Failed to update preference: {message}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to update preference: {e}")
            return False
    
    def update_multiple_preferences(self, user_id: str, preferences_data: Dict[str, Any]) -> bool:
        """Update multiple preferences.
        
        Args:
            user_id: User ID
            preferences_data: Dictionary of preferences to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            preferences = self.auth_service.get_user_preferences(user_id)
            if not preferences:
                preferences = UserPreferences.create_default(user_id)
            
            # Update multiple preferences
            for key, value in preferences_data.items():
                preferences.set_preference(key, value)
            
            success, message = self.auth_service.update_user_preferences(
                user_id, preferences
            )
            
            if success:
                self.logger.info(f"Multiple preferences updated for user {user_id}")
                return True
            else:
                self.logger.error(f"Failed to update preferences: {message}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to update multiple preferences: {e}")
            return False
    
    def get_default_agent(self, user_id: str) -> str:
        """Get user's default agent preference.
        
        Args:
            user_id: User ID
            
        Returns:
            Default agent ID
        """
        try:
            preferences = self.auth_service.get_user_preferences(user_id)
            if not preferences:
                return "auto"
            
            return preferences.get_preference("default_agent", "auto")
            
        except Exception as e:
            self.logger.error(f"Failed to get default agent: {e}")
            return "auto"
    
    def set_default_agent(self, user_id: str, agent_id: str) -> bool:
        """Set user's default agent preference.
        
        Args:
            user_id: User ID
            agent_id: Agent ID to set as default
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return self.update_preference(user_id, "default_agent", agent_id)
        except Exception as e:
            self.logger.error(f"Failed to set default agent: {e}")
            return False
    
    def get_theme(self, user_id: str) -> str:
        """Get user's theme preference.
        
        Args:
            user_id: User ID
            
        Returns:
            Theme name
        """
        try:
            preferences = self.auth_service.get_user_preferences(user_id)
            if not preferences:
                return "light"
            
            return preferences.get_preference("theme", "light")
            
        except Exception as e:
            self.logger.error(f"Failed to get theme: {e}")
            return "light"
    
    def set_theme(self, user_id: str, theme: str) -> bool:
        """Set user's theme preference.
        
        Args:
            user_id: User ID
            theme: Theme name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return self.update_preference(user_id, "theme", theme)
        except Exception as e:
            self.logger.error(f"Failed to set theme: {e}")
            return False
