"""GitHub OAuth integration for ExplainStack."""

import os
import logging
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlencode, parse_qs, urlparse

logger = logging.getLogger(__name__)


class GitHubOAuthProvider:
    """GitHub OAuth provider for ExplainStack."""
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize GitHub OAuth provider.
        
        Args:
            client_id: GitHub OAuth client ID
            client_secret: GitHub OAuth client secret
        """
        self.client_id = client_id or os.getenv('GITHUB_OAUTH_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('GITHUB_OAUTH_CLIENT_SECRET')
        self.redirect_uri = os.getenv('GITHUB_OAUTH_REDIRECT_URI', 'http://localhost:8000/oauth/github/callback')
        self.scope = 'user:email'
        
        if not self.client_id:
            logger.warning("GitHub OAuth client ID not configured")
        if not self.client_secret:
            logger.warning("GitHub OAuth client secret not configured")
    
    def get_authorization_url(self, state: str) -> str:
        """Get GitHub OAuth authorization URL.
        
        Args:
            state: State parameter for security
            
        Returns:
            Authorization URL
        """
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
            'state': state
        }
        
        base_url = 'https://github.com/login/oauth/authorize'
        return f"{base_url}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Exchange authorization code for access token.
        
        Args:
            code: Authorization code from GitHub
            
        Returns:
            Tuple of (success, token_data, error_message)
        """
        try:
            import requests
            
            token_url = 'https://github.com/login/oauth/access_token'
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code
            }
            headers = {'Accept': 'application/json'}
            
            response = requests.post(token_url, data=data, headers=headers)
            
            if response.status_code == 200:
                token_data = response.json()
                return True, token_data, None
            else:
                return False, None, f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            return False, None, f"Error: {str(e)}"
    
    def get_user_info(self, access_token: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Get user information from GitHub.
        
        Args:
            access_token: GitHub access token
            
        Returns:
            Tuple of (success, user_info, error_message)
        """
        try:
            import requests
            
            user_info_url = 'https://api.github.com/user'
            headers = {'Authorization': f'token {access_token}'}
            
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
        """Check if GitHub OAuth is properly configured.
        
        Returns:
            True if configured, False otherwise
        """
        return bool(self.client_id and self.client_secret)
    
    def get_setup_instructions(self) -> str:
        """Get setup instructions for GitHub OAuth.
        
        Returns:
            Setup instructions string
        """
        return """🔧 **GitHub OAuth Setup Instructions**

1. **Go to GitHub Settings**: https://github.com/settings/developers
2. **Create a new OAuth App**:
   - Click "New OAuth App"
   - Fill in the form:
     - **Application name**: ExplainStack
     - **Homepage URL**: https://yourdomain.com
     - **Authorization callback URL**: http://localhost:8000/oauth/github/callback
3. **Get your credentials**:
   - Copy the "Client ID" and "Client Secret"
4. **Set environment variables**:
   ```bash
   export GITHUB_OAUTH_CLIENT_ID="your-client-id"
   export GITHUB_OAUTH_CLIENT_SECRET="your-client-secret"
   export GITHUB_OAUTH_REDIRECT_URI="http://localhost:8000/oauth/github/callback"
   ```

**Note**: Replace `your-client-id` and `your-client-secret` with your actual credentials."""
