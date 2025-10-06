"""Gerrit integration for ExplainStack."""

import re
import logging
import requests
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)


class GerritIntegration:
    """Integration with Gerrit code review system."""
    
    def __init__(self, base_url: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None, api_token: Optional[str] = None):
        """Initialize Gerrit integration.
        
        Args:
            base_url: Gerrit base URL (e.g., 'https://review.opendev.org')
            username: Gerrit username for authentication
            password: Gerrit password for authentication
            api_token: Gerrit API token (alternative to username/password)
        """
        self.base_url = base_url or "https://review.opendev.org"
        self.username = username
        self.password = password
        self.api_token = api_token
        self.session = requests.Session()
        
        # Configure authentication (but don't force it for public endpoints)
        self.has_auth = False
        if api_token:
            self.has_auth = True
            # Store token for later use if needed
            self._stored_token = api_token
        elif username and password:
            self.has_auth = True
            # Store credentials for later use if needed
            self._stored_username = username
            self._stored_password = password
        
        # Set default headers for Gerrit API
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'ExplainStack/1.0'
        })
    
    def _apply_auth(self):
        """Apply authentication to the session if available."""
        if hasattr(self, '_stored_token') and self._stored_token:
            # Try token as username with empty password
            self.session.auth = (self._stored_token, '')
        elif hasattr(self, '_stored_username') and hasattr(self, '_stored_password'):
            # Use username/password
            self.session.auth = (self._stored_username, self._stored_password)
    
    def parse_gerrit_url(self, url: str) -> Optional[Dict[str, str]]:
        """Parse Gerrit URL to extract change information.
        
        Args:
            url: Gerrit URL (e.g., 'https://review.opendev.org/c/openstack/nova/+/12345')
            
        Returns:
            Dictionary with change information or None if invalid
        """
        try:
            # Pattern for Gerrit URLs
            patterns = [
                r'https?://([^/]+)/c/([^/]+)/([^/]+)/\+/(\d+)',
                r'https?://([^/]+)/c/([^/]+)/\+/(\d+)',
                r'https?://([^/]+)/#/c/([^/]+)/([^/]+)/\+/(\d+)',
                r'https?://([^/]+)/#/c/([^/]+)/\+/(\d+)'
            ]
            
            for pattern in patterns:
                match = re.match(pattern, url)
                if match:
                    groups = match.groups()
                    if len(groups) == 4:
                        return {
                            'host': groups[0],
                            'project': groups[1],
                            'branch': groups[2],
                            'change_id': groups[3]
                        }
                    elif len(groups) == 3:
                        return {
                            'host': groups[0],
                            'project': groups[1],
                            'change_id': groups[2]
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing Gerrit URL {url}: {e}")
            return None
    
    def test_authentication(self) -> Tuple[bool, Optional[str]]:
        """Test Gerrit authentication.
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Try to access a simple endpoint that requires authentication
            url = f"{self.base_url}/a/accounts/self"
            response = self.session.get(url)
            
            if response.status_code == 200:
                return True, None
            elif response.status_code == 401:
                return False, "Authentication required but not configured"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            logger.error(f"Error testing authentication: {e}")
            return False, f"Error: {str(e)}"
    
    def is_authenticated(self) -> bool:
        """Check if Gerrit integration is authenticated.
        
        Returns:
            True if authenticated, False otherwise
        """
        return bool(self.username and self.password) or bool(self.api_token)
    
    def get_change_info(self, change_id: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Get change information from Gerrit.
        
        Args:
            change_id: Gerrit change ID
            
        Returns:
            Tuple of (success, change_info, error_message)
        """
        try:
            # Try authenticated endpoint first
            if self.is_authenticated():
                url = f"{self.base_url}/a/changes/{change_id}"
            else:
                # Try public endpoint (some Gerrit instances allow this)
                url = f"{self.base_url}/changes/{change_id}"
            
            response = self.session.get(url, headers={'Accept': 'application/json'})
            
            if response.status_code == 200:
                # Remove Gerrit's magic prefix
                content = response.text
                if content.startswith(')]}\''):
                    content = content[4:]
                
                import json
                change_info = json.loads(content)
                return True, change_info, None
            elif response.status_code == 401:
                # Try public endpoint if authenticated failed
                if self.is_authenticated():
                    public_url = f"{self.base_url}/changes/{change_id}"
                    public_response = self.session.get(public_url, headers={'Accept': 'application/json'})
                    if public_response.status_code == 200:
                        content = public_response.text
                        if content.startswith(')]}\''):
                            content = content[4:]
                        import json
                        change_info = json.loads(content)
                        return True, change_info, None
                
                return False, None, "Authentication required. Please configure Gerrit credentials."
            else:
                return False, None, f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            logger.error(f"Error getting change info for {change_id}: {e}")
            return False, None, f"Error: {str(e)}"
    
    def get_change_diff(self, change_id: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Get change diff from Gerrit.
        
        Args:
            change_id: Gerrit change ID
            
        Returns:
            Tuple of (success, diff_content, error_message)
        """
        try:
            # Try public endpoint first (no authentication required)
            public_url = f"{self.base_url}/c/changes/{change_id}/revisions/current/patch"
            response = self.session.get(public_url, headers={'Accept': 'text/plain'})
            
            if response.status_code == 200:
                return True, response.text, None
            
            # If public endpoint fails and we have auth, try authenticated endpoint
            if self.has_auth:
                self._apply_auth()
                auth_url = f"{self.base_url}/a/changes/{change_id}/revisions/current/patch"
                response = self.session.get(auth_url, headers={'Accept': 'text/plain'})
                
                if response.status_code == 200:
                    return True, response.text, None
                else:
                    return False, None, f"HTTP {response.status_code}: {response.text}"
            else:
                return False, None, f"HTTP {response.status_code}: {response.text} (Authentication may be required)"
                
        except Exception as e:
            logger.error(f"Error getting diff for {change_id}: {e}")
            return False, None, f"Error: {str(e)}"
    
    def get_change_comments(self, change_id: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Get change comments from Gerrit.
        
        Args:
            change_id: Gerrit change ID
            
        Returns:
            Tuple of (success, comments, error_message)
        """
        try:
            # Gerrit REST API endpoint for comments
            url = f"{self.base_url}/a/changes/{change_id}/comments"
            
            response = self.session.get(url, headers={'Accept': 'application/json'})
            
            if response.status_code == 200:
                # Remove Gerrit's magic prefix
                content = response.text
                if content.startswith(')]}\''):
                    content = content[4:]
                
                import json
                comments = json.loads(content)
                return True, comments, None
            else:
                return False, None, f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            logger.error(f"Error getting comments for {change_id}: {e}")
            return False, None, f"Error: {str(e)}"
    
    def analyze_gerrit_url(self, url: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Analyze a Gerrit URL and return comprehensive information.
        
        Args:
            url: Gerrit URL
            
        Returns:
            Tuple of (success, analysis_result, error_message)
        """
        try:
            # Parse URL
            url_info = self.parse_gerrit_url(url)
            if not url_info:
                return False, None, "Invalid Gerrit URL format"
            
            change_id = url_info.get('change_id')
            if not change_id:
                return False, None, "Could not extract change ID from URL"
            
            # Get change information
            success, change_info, error = self.get_change_info(change_id)
            if not success:
                return False, None, f"Failed to get change info: {error}"
            
            # Get diff
            success, diff_content, error = self.get_change_diff(change_id)
            if not success:
                return False, None, f"Failed to get diff: {error}"
            
            # Get comments
            success, comments, error = self.get_change_comments(change_id)
            if not success:
                logger.warning(f"Failed to get comments: {error}")
                comments = {}
            
            # Compile analysis result
            analysis_result = {
                'url_info': url_info,
                'change_info': change_info,
                'diff_content': diff_content,
                'comments': comments,
                'summary': {
                    'subject': change_info.get('subject', ''),
                    'status': change_info.get('status', ''),
                    'project': change_info.get('project', ''),
                    'branch': change_info.get('branch', ''),
                    'owner': change_info.get('owner', {}).get('name', 'Unknown'),
                    'created': change_info.get('created', ''),
                    'updated': change_info.get('updated', ''),
                    'insertions': change_info.get('insertions', 0),
                    'deletions': change_info.get('deletions', 0),
                    'files_changed': len(change_info.get('files', {}))
                }
            }
            
            return True, analysis_result, None
            
        except Exception as e:
            logger.error(f"Error analyzing Gerrit URL {url}: {e}")
            return False, None, f"Error: {str(e)}"
    
    def format_gerrit_analysis(self, analysis_result: Dict[str, Any]) -> str:
        """Format Gerrit analysis result for display.
        
        Args:
            analysis_result: Analysis result from analyze_gerrit_url
            
        Returns:
            Formatted string for display
        """
        try:
            summary = analysis_result.get('summary', {})
            change_info = analysis_result.get('change_info', {})
            diff_content = analysis_result.get('diff_content', '')
            
            # Format basic information
            result = f"""🔍 **Gerrit Change Analysis**

**Change Information:**
- **Subject**: {summary.get('subject', 'N/A')}
- **Status**: {summary.get('status', 'N/A')}
- **Project**: {summary.get('project', 'N/A')}
- **Branch**: {summary.get('branch', 'N/A')}
- **Owner**: {summary.get('owner', 'N/A')}
- **Created**: {summary.get('created', 'N/A')}
- **Updated**: {summary.get('updated', 'N/A')}

**Statistics:**
- **Insertions**: {summary.get('insertions', 0)} lines
- **Deletions**: {summary.get('deletions', 0)} lines
- **Files Changed**: {summary.get('files_changed', 0)} files

**Description:**
{change_info.get('subject', 'No description available')}

**Diff Preview:**
```diff
{diff_content[:1000]}{'...' if len(diff_content) > 1000 else ''}
```

**What would you like to do with this change?**
- Type `review` to analyze the patch
- Type `security` to check for security issues
- Type `performance` to analyze performance impact
- Type `commit message` to generate a commit message
- Or ask me anything about this change!"""
            
            return result
            
        except Exception as e:
            logger.error(f"Error formatting Gerrit analysis: {e}")
            return f"Error formatting analysis: {str(e)}"
    
    def is_gerrit_url(self, text: str) -> bool:
        """Check if text is a Gerrit URL.
        
        Args:
            text: Text to check
            
        Returns:
            True if text is a Gerrit URL
        """
        gerrit_patterns = [
            r'https?://[^/]+/c/[^/]+/[^/]+/\+/\d+',
            r'https?://[^/]+/c/[^/]+/\+/\d+',
            r'https?://[^/]+/#/c/[^/]+/[^/]+/\+/\d+',
            r'https?://[^/]+/#/c/[^/]+/\+/\d+'
        ]
        
        for pattern in gerrit_patterns:
            if re.match(pattern, text):
                return True
        
        return False
