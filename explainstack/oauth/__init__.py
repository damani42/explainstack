"""OAuth integration for ExplainStack."""

from .google_oauth import GoogleOAuthProvider
from .github_oauth import GitHubOAuthProvider
from .oauth_manager import OAuthManager

__all__ = ['GoogleOAuthProvider', 'GitHubOAuthProvider', 'OAuthManager']
