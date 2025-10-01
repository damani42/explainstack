"""Google OAuth integration for ExplainStack."""

import os
import logging
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlencode, parse_qs, urlparse

logger = logging.getLogger(__name__)


class GoogleOAuthProvider:
    """Google OAuth provider for ExplainStack."""
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize Google OAuth provider.
        
        Args:
            client_id: Google OAuth client ID
            client_secret: Google OAuth client secret
        """
        self.client_id = client_id or os.getenv('GOOGLE_OAUTH_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')
        self.redirect_uri = os.getenv('GOOGLE_OAUTH_REDIRECT_URI', 'http://localhost:8000/oauth/google/callback')
        self.scope = 'openid email profile'
        
        if not self.client_id:
            logger.warning("Google OAuth client ID not configured")
        if not self.client_secret:
            logger.warning("Google OAuth client secret not configured")
    
    def get_authorization_url(self, state: str) -> str:
        """Get Google OAuth authorization URL.
        
        Args:
            state: State parameter for security
            
        Returns:
            Authorization URL
        """
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
            'response_type': 'code',
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        base_url = 'https://accounts.google.com/o/oauth2/v2/auth'
        return f"{base_url}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Exchange authorization code for access token.
        
        Args:
            code: Authorization code from Google
            
        Returns:
            Tuple of (success, token_data, error_message)
        """
        try:
            import requests
            
            token_url = 'https://oauth2.googleapis.com/token'
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri
            }
            
            response = requests.post(token_url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                return True, token_data, None
            else:
                return False, None, f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            return False, None, f"Error: {str(e)}"
    
    def get_user_info(self, access_token: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Get user information from Google.
        
        Args:
            access_token: Google access token
            
        Returns:
            Tuple of (success, user_info, error_message)
        """
        try:
            import requests
            
            user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
            headers = {'Authorization': f'Bearer {access_token}'}
            
            response = requests.get(user_info_url, headers=headers)
            
            if response.status_code == 200:
                user_info = response.json()
                return True, user_info, None
            else:
                return False, None, f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return False, None, f"Error: {str(e)}"
    
    def is_configured(self) -> bool:
        """Check if Google OAuth is properly configured.
        
        Returns:
            True if configured, False otherwise
        """
        return bool(self.client_id and self.client_secret)
    
    def get_setup_instructions(self) -> str:
        """Get setup instructions for Google OAuth.
        
        Returns:
            Setup instructions string
        """
        return """🔧 **Google OAuth Setup Instructions**

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create a new project** or select existing one
3. **Enable Google+ API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API" and enable it
4. **Create OAuth 2.0 credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client ID"
   - Choose "Web application"
   - Add authorized redirect URIs:
     - `http://localhost:8000/oauth/google/callback` (for development)
     - `https://yourdomain.com/oauth/google/callback` (for production)
5. **Set environment variables**:
   ```bash
   export GOOGLE_OAUTH_CLIENT_ID="your-client-id"
   export GOOGLE_OAUTH_CLIENT_SECRET="your-client-secret"
   export GOOGLE_OAUTH_REDIRECT_URI="http://localhost:8000/oauth/google/callback"
   ```

**Note**: Replace `your-client-id` and `your-client-secret` with your actual credentials."""
