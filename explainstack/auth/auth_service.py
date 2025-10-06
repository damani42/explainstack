"""Authentication service for ExplainStack."""

import logging
from typing import Optional, Tuple
from datetime import datetime, timedelta
from ..database import DatabaseManager, User, UserSession, UserPreferences

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service for ExplainStack."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize authentication service.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
    
    def register_user(self, email: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """Register a new user.
        
        Args:
            email: User email
            password: Plain text password
            
        Returns:
            Tuple of (success, message, user)
        """
        try:
            # Validate email format
            if not self._is_valid_email(email):
                return False, "Invalid email format", None
            
            # Validate password strength
            if not self._is_valid_password(password):
                return False, "Password must be at least 8 characters long", None
            
            # Check if user already exists
            existing_user = self.db.get_user_by_email(email)
            if existing_user:
                return False, "Email already registered", None
            
            # Create user
            user = self.db.create_user(email, password)
            self.logger.info(f"User registered: {email}")
            
            return True, "User registered successfully", user
            
        except Exception as e:
            self.logger.error(f"Registration failed: {e}")
            return False, f"Registration failed: {str(e)}", None
    
    def login_user(self, email: str, password: str) -> Tuple[bool, str, Optional[UserSession]]:
        """Login a user.
        
        Args:
            email: User email
            password: Plain text password
            
        Returns:
            Tuple of (success, message, session)
        """
        try:
            # Get user by email
            user = self.db.get_user_by_email(email)
            if not user:
                return False, "Invalid email or password", None
            
            # Verify password
            if not user.verify_password(password):
                return False, "Invalid email or password", None
            
            # Create session
            session = self.db.create_session(user.user_id)
            self.logger.info(f"User logged in: {email}")
            
            return True, "Login successful", session
            
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            return False, f"Login failed: {str(e)}", None
    
    def logout_user(self, session_id: str) -> Tuple[bool, str]:
        """Logout a user.
        
        Args:
            session_id: Session ID
            
        Returns:
            Tuple of (success, message)
        """
        try:
            self.db.invalidate_session(session_id)
            self.logger.info(f"User logged out: {session_id}")
            return True, "Logout successful"
            
        except Exception as e:
            self.logger.error(f"Logout failed: {e}")
            return False, f"Logout failed: {str(e)}"
    
    def get_user_from_session(self, session_id: str) -> Optional[User]:
        """Get user from session ID.
        
        Args:
            session_id: Session ID
            
        Returns:
            User instance or None if session invalid
        """
        try:
            session = self.db.get_session(session_id)
            if not session:
                return None
            
            user = self.db.get_user_by_id(session.user_id)
            return user
            
        except Exception as e:
            self.logger.error(f"Failed to get user from session: {e}")
            return None
    
    def get_user_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """Get user preferences.
        
        Args:
            user_id: User ID
            
        Returns:
            UserPreferences instance or None if not found
        """
        try:
            return self.db.get_user_preferences(user_id)
        except Exception as e:
            self.logger.error(f"Failed to get user preferences: {e}")
            return None
    
    def update_user_preferences(self, user_id: str, preferences: UserPreferences) -> Tuple[bool, str]:
        """Update user preferences.
        
        Args:
            user_id: User ID
            preferences: UserPreferences instance
            
        Returns:
            Tuple of (success, message)
        """
        try:
            success, message = self.db.update_user_preferences(user_id, preferences)
            if success:
                self.logger.info(f"Preferences updated for user: {user_id}")
            else:
                self.logger.error(f"Failed to update preferences: {message}")
            return success, message
            
        except Exception as e:
            self.logger.error(f"Failed to update preferences: {e}")
            return False, f"Failed to update preferences: {str(e)}"
    
    def is_session_valid(self, session_id: str) -> bool:
        """Check if session is valid.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if session is valid, False otherwise
        """
        try:
            session = self.db.get_session(session_id)
            return session is not None
        except Exception as e:
            self.logger.error(f"Failed to validate session: {e}")
            return False
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Validate email format.
        
        Args:
            email: Email to validate
            
        Returns:
            True if valid, False otherwise
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def _is_valid_password(password: str) -> bool:
        """Validate password strength.
        
        Args:
            password: Password to validate
            
        Returns:
            True if valid, False otherwise
        """
        return len(password) >= 8
