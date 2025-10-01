"""OAuth manager for ExplainStack."""

import os
import secrets
import logging
from typing import Dict, Any, Optional, Tuple
from .google_oauth import GoogleOAuthProvider
from .github_oauth import GitHubOAuthProvider

logger = logging.getLogger(__name__)


class OAuthManager:
    """Central OAuth manager for ExplainStack."""
    
    def __init__(self):
        """Initialize OAuth manager."""
        self.google_provider = GoogleOAuthProvider()
        self.github_provider = GitHubOAuthProvider()
        self.state_store = {}  # In production, use Redis or database
    
    def get_available_providers(self) -> Dict[str, Dict[str, Any]]:
        """Get available OAuth providers.
        
        Returns:
            Dictionary of available providers
        """
        providers = {}
        
        if self.google_provider.is_configured():
            providers['google'] = {
                'name': 'Google',
                'icon': '🔵',
                'description': 'Sign in with Google',
                'configured': True
            }
        else:
            providers['google'] = {
                'name': 'Google',
                'icon': '🔵',
                'description': 'Sign in with Google (not configured)',
                'configured': False
            }
        
        if self.github_provider.is_configured():
            providers['github'] = {
                'name': 'GitHub',
                'icon': '⚫',
                'description': 'Sign in with GitHub',
                'configured': True
            }
        else:
            providers['github'] = {
                'name': 'GitHub',
                'icon': '⚫',
                'description': 'Sign in with GitHub (not configured)',
                'configured': False
            }
        
        return providers
    
    def generate_state(self, user_id: str) -> str:
        """Generate OAuth state for security.
        
        Args:
            user_id: User identifier
            
        Returns:
            OAuth state string
        """
        state = secrets.token_urlsafe(32)
        self.state_store[state] = {
            'user_id': user_id,
            'timestamp': os.time.time()
        }
        return state
    
    def validate_state(self, state: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Validate OAuth state.
        
        Args:
            state: OAuth state string
            
        Returns:
            Tuple of (is_valid, user_id, error_message)
        """
        if state not in self.state_store:
            return False, None, "Invalid OAuth state"
        
        state_data = self.state_store[state]
        
        # Check if state is expired (5 minutes)
        import time
        if time.time() - state_data['timestamp'] > 300:
            del self.state_store[state]
            return False, None, "OAuth state expired"
        
        user_id = state_data['user_id']
        del self.state_store[state]
        
        return True, user_id, None
    
    def get_authorization_url(self, provider: str, user_id: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Get OAuth authorization URL.
        
        Args:
            provider: OAuth provider name
            user_id: User identifier
            
        Returns:
            Tuple of (success, authorization_url, error_message)
        """
        try:
            state = self.generate_state(user_id)
            
            if provider == 'google':
                if not self.google_provider.is_configured():
                    return False, None, "Google OAuth not configured"
                url = self.google_provider.get_authorization_url(state)
                return True, url, None
            
            elif provider == 'github':
                if not self.github_provider.is_configured():
                    return False, None, "GitHub OAuth not configured"
                url = self.github_provider.get_authorization_url(state)
                return True, url, None
            
            else:
                return False, None, f"Unknown OAuth provider: {provider}"
                
        except Exception as e:
            logger.error(f"Error getting authorization URL for {provider}: {e}")
            return False, None, f"Error: {str(e)}"
    
    def handle_oauth_callback(self, provider: str, code: str, state: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Handle OAuth callback.
        
        Args:
            provider: OAuth provider name
            code: Authorization code
            state: OAuth state
            
        Returns:
            Tuple of (success, user_data, error_message)
        """
        try:
            # Validate state
            is_valid, user_id, error = self.validate_state(state)
            if not is_valid:
                return False, None, error
            
            # Exchange code for token
            if provider == 'google':
                success, token_data, error = self.google_provider.exchange_code_for_token(code)
                if not success:
                    return False, None, error
                
                # Get user info
                success, user_info, error = self.google_provider.get_user_info(token_data['access_token'])
                if not success:
                    return False, None, error
                
                # Format user data
                user_data = {
                    'provider': 'google',
                    'provider_id': user_info['id'],
                    'email': user_info['email'],
                    'name': user_info['name'],
                    'avatar_url': user_info['picture'],
                    'access_token': token_data['access_token'],
                    'refresh_token': token_data.get('refresh_token')
                }
                
                return True, user_data, None
            
            elif provider == 'github':
                success, token_data, error = self.github_provider.exchange_code_for_token(code)
                if not success:
                    return False, None, error
                
                # Get user info
                success, user_info, error = self.github_provider.get_user_info(token_data['access_token'])
                if not success:
                    return False, None, error
                
                # Format user data
                user_data = {
                    'provider': 'github',
                    'provider_id': str(user_info['id']),
                    'email': user_info['email'],
                    'name': user_info['name'],
                    'avatar_url': user_info['avatar_url'],
                    'access_token': token_data['access_token']
                }
                
                return True, user_data, None
            
            else:
                return False, None, f"Unknown OAuth provider: {provider}"
                
        except Exception as e:
            logger.error(f"Error handling OAuth callback for {provider}: {e}")
            return False, None, f"Error: {str(e)}"
    
    def get_setup_instructions(self) -> str:
        """Get setup instructions for all OAuth providers.
        
        Returns:
            Setup instructions string
        """
        instructions = "🔧 **OAuth Setup Instructions**\n\n"
        
        if not self.google_provider.is_configured():
            instructions += "**Google OAuth:**\n"
            instructions += self.google_provider.get_setup_instructions()
            instructions += "\n\n"
        
        if not self.github_provider.is_configured():
            instructions += "**GitHub OAuth:**\n"
            instructions += self.github_provider.get_setup_instructions()
            instructions += "\n\n"
        
        if self.google_provider.is_configured() and self.github_provider.is_configured():
            instructions += "✅ **All OAuth providers are configured!**"
        
        return instructions
