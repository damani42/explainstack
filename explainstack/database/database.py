"""Database manager for ExplainStack user system."""

import sqlite3
import json
import logging
from typing import Optional, List, Tuple
from datetime import datetime
from .models import User, UserSession, UserPreferences

logger = logging.getLogger(__name__)


class DatabaseManager:
    """SQLite database manager for ExplainStack."""
    
    def __init__(self, db_path: str = "explainstack.db"):
        """Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id TEXT PRIMARY KEY,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        is_active BOOLEAN DEFAULT 1
                    )
                """)
                
                # Create sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        session_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        expires_at TIMESTAMP NOT NULL,
                        is_active BOOLEAN DEFAULT 1,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                """)
                
                # Create user preferences table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        user_id TEXT PRIMARY KEY,
                        preferences TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                """)
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def create_user(self, email: str, password: str) -> User:
        """Create a new user.
        
        Args:
            email: User email
            password: Plain text password
            
        Returns:
            Created User instance
            
        Raises:
            ValueError: If email already exists
        """
        try:
            user = User.create(email, password)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (user_id, email, password_hash, created_at, is_active)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    user.user_id,
                    user.email,
                    user.password_hash,
                    user.created_at,
                    user.is_active
                ))
                
                # Create default preferences
                preferences = UserPreferences.create_default(user.user_id)
                cursor.execute("""
                    INSERT INTO user_preferences (user_id, preferences)
                    VALUES (?, ?)
                """, (
                    preferences.user_id,
                    json.dumps(preferences.to_dict()['preferences'])
                ))
                
                conn.commit()
                self.logger.info(f"User created: {email}")
                return user
                
        except sqlite3.IntegrityError:
            raise ValueError("Email already exists")
        except Exception as e:
            self.logger.error(f"Failed to create user: {e}")
            raise
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User instance or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_id, email, password_hash, created_at, is_active
                    FROM users WHERE email = ? AND is_active = 1
                """, (email,))
                
                row = cursor.fetchone()
                if row:
                    return User(
                        user_id=row[0],
                        email=row[1],
                        password_hash=row[2],
                        created_at=datetime.fromisoformat(row[3]),
                        is_active=bool(row[4])
                    )
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get user by email: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User instance or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_id, email, password_hash, created_at, is_active
                    FROM users WHERE user_id = ? AND is_active = 1
                """, (user_id,))
                
                row = cursor.fetchone()
                if row:
                    return User(
                        user_id=row[0],
                        email=row[1],
                        password_hash=row[2],
                        created_at=datetime.fromisoformat(row[3]),
                        is_active=bool(row[4])
                    )
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get user by ID: {e}")
            return None
    
    def create_session(self, user_id: str, duration_hours: int = 24) -> UserSession:
        """Create a new user session.
        
        Args:
            user_id: User ID
            duration_hours: Session duration in hours
            
        Returns:
            Created UserSession instance
        """
        try:
            session = UserSession.create(user_id, duration_hours)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_sessions (session_id, user_id, created_at, expires_at, is_active)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    session.session_id,
                    session.user_id,
                    session.created_at,
                    session.expires_at,
                    session.is_active
                ))
                
                conn.commit()
                self.logger.info(f"Session created for user: {user_id}")
                return session
                
        except Exception as e:
            self.logger.error(f"Failed to create session: {e}")
            raise
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get session by ID.
        
        Args:
            session_id: Session ID
            
        Returns:
            UserSession instance or None if not found/expired
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT session_id, user_id, created_at, expires_at, is_active
                    FROM user_sessions 
                    WHERE session_id = ? AND is_active = 1
                """, (session_id,))
                
                row = cursor.fetchone()
                if row:
                    session = UserSession(
                        session_id=row[0],
                        user_id=row[1],
                        created_at=datetime.fromisoformat(row[2]),
                        expires_at=datetime.fromisoformat(row[3]),
                        is_active=bool(row[4])
                    )
                    
                    # Check if expired
                    if session.is_expired():
                        self.invalidate_session(session_id)
                        return None
                    
                    return session
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get session: {e}")
            return None
    
    def invalidate_session(self, session_id: str):
        """Invalidate a session.
        
        Args:
            session_id: Session ID to invalidate
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE user_sessions 
                    SET is_active = 0 
                    WHERE session_id = ?
                """, (session_id,))
                
                conn.commit()
                self.logger.info(f"Session invalidated: {session_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to invalidate session: {e}")
    
    def get_user_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """Get user preferences.
        
        Args:
            user_id: User ID
            
        Returns:
            UserPreferences instance or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT preferences FROM user_preferences WHERE user_id = ?
                """, (user_id,))
                
                row = cursor.fetchone()
                if row:
                    preferences = json.loads(row[0])
                    return UserPreferences(user_id, preferences)
                return None
                
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
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE user_preferences 
                    SET preferences = ? 
                    WHERE user_id = ?
                """, (json.dumps(preferences.preferences), user_id))
                
                if cursor.rowcount == 0:
                    return False, "User preferences not found"
                
                conn.commit()
                self.logger.info(f"Preferences updated for user: {user_id}")
                return True, "Preferences updated successfully"
                
        except Exception as e:
            self.logger.error(f"Failed to update preferences: {e}")
            return False, f"Failed to update preferences: {str(e)}"
