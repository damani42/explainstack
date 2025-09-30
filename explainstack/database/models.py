"""Database models for ExplainStack user system."""

import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json


class User:
    """User model for ExplainStack."""
    
    def __init__(self, user_id: str, email: str, password_hash: str, 
                 created_at: datetime, is_active: bool = True):
        self.user_id = user_id
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at
        self.is_active = is_active
    
    @classmethod
    def create(cls, email: str, password: str) -> 'User':
        """Create a new user.
        
        Args:
            email: User email
            password: Plain text password
            
        Returns:
            New User instance
        """
        user_id = secrets.token_urlsafe(16)
        password_hash = cls._hash_password(password)
        created_at = datetime.utcnow()
        
        return cls(
            user_id=user_id,
            email=email,
            password_hash=password_hash,
            created_at=created_at,
            is_active=True
        )
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash a password using SHA-256 with salt."""
        salt = secrets.token_hex(16)
        return hashlib.sha256((password + salt).encode()).hexdigest() + ':' + salt
    
    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        try:
            stored_hash, salt = self.password_hash.split(':')
            test_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return test_hash == stored_hash
        except ValueError:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        return {
            'user_id': self.user_id,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }


class UserSession:
    """User session model."""
    
    def __init__(self, session_id: str, user_id: str, created_at: datetime, 
                 expires_at: datetime, is_active: bool = True):
        self.session_id = session_id
        self.user_id = user_id
        self.created_at = created_at
        self.expires_at = expires_at
        self.is_active = is_active
    
    @classmethod
    def create(cls, user_id: str, duration_hours: int = 24) -> 'UserSession':
        """Create a new session.
        
        Args:
            user_id: User ID
            duration_hours: Session duration in hours
            
        Returns:
            New UserSession instance
        """
        session_id = secrets.token_urlsafe(32)
        created_at = datetime.utcnow()
        expires_at = created_at + timedelta(hours=duration_hours)
        
        return cls(
            session_id=session_id,
            user_id=user_id,
            created_at=created_at,
            expires_at=expires_at,
            is_active=True
        )
    
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'is_active': self.is_active
        }


class UserPreferences:
    """User preferences model."""
    
    def __init__(self, user_id: str, preferences: Dict[str, Any]):
        self.user_id = user_id
        self.preferences = preferences
    
    @classmethod
    def create_default(cls, user_id: str) -> 'UserPreferences':
        """Create default preferences for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            New UserPreferences instance with defaults
        """
        default_prefs = {
            'default_agent': 'auto',
            'openai_api_key': '',
            'claude_api_key': '',
            'gemini_api_key': '',
            'preferred_models': {
                'code_expert': 'gpt-4',
                'patch_reviewer': 'claude-3-sonnet-20240229',
                'import_cleaner': 'gpt-3.5-turbo',
                'commit_writer': 'gpt-4'
            },
            'theme': 'light',
            'language': 'en',
            'notifications': True
        }
        
        return cls(user_id=user_id, preferences=default_prefs)
    
    def get_preference(self, key: str, default=None):
        """Get a preference value."""
        return self.preferences.get(key, default)
    
    def set_preference(self, key: str, value: Any):
        """Set a preference value."""
        self.preferences[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert preferences to dictionary."""
        return {
            'user_id': self.user_id,
            'preferences': self.preferences
        }
