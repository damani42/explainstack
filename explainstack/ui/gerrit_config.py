"""Gerrit configuration UI for ExplainStack."""

import chainlit as cl
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class GerritConfigUI:
    """UI for configuring Gerrit integration."""
    
    def __init__(self):
        self.config_key = "gerrit_config"
    
    async def show_config_ui(self):
        """Show Gerrit configuration interface."""
        try:
            # Get current configuration
            current_config = cl.user_session.get(self.config_key, {})
            
            config_message = f"""🔧 **Gerrit Configuration**

**Current Settings:**
- **Base URL**: {current_config.get('base_url', 'https://review.opendev.org')}
- **Authentication**: {'✅ Configured' if current_config.get('username') or current_config.get('api_token') else '❌ Not configured'}
- **Username**: {current_config.get('username', 'Not set')}
- **API Token**: {'✅ Set' if current_config.get('api_token') else '❌ Not set'}

**Configuration Options:**
1. **Set Base URL** - Configure Gerrit server URL
2. **Set Username/Password** - Basic authentication
3. **Set API Token** - Token-based authentication
4. **Test Connection** - Verify configuration
5. **Clear Configuration** - Reset settings

**Note**: For OpenStack Gerrit (review.opendev.org), you can often access public changes without authentication, but authentication provides access to more features and private changes.

Type the number of the option you want to configure, or type 'back' to return to the main menu."""
            
            await cl.Message(content=config_message).send()
            
        except Exception as e:
            logger.error(f"Error showing Gerrit config UI: {e}")
            await cl.Message(content="❌ Error loading Gerrit configuration. Please try again.").send()
    
    async def handle_config_option(self, option: str) -> bool:
        """Handle Gerrit configuration option.
        
        Args:
            option: Selected configuration option
            
        Returns:
            True if configuration was updated, False otherwise
        """
        try:
            current_config = cl.user_session.get(self.config_key, {})
            
            if option == "1":
                await self._configure_base_url(current_config)
            elif option == "2":
                await self._configure_username_password(current_config)
            elif option == "3":
                await self._configure_api_token(current_config)
            elif option == "4":
                await self._test_connection(current_config)
            elif option == "5":
                await self._clear_configuration()
            else:
                await cl.Message(content="❌ Invalid option. Please try again.").send()
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling Gerrit config option {option}: {e}")
            await cl.Message(content="❌ Error processing configuration. Please try again.").send()
            return False
    
    async def _configure_base_url(self, current_config: Dict[str, Any]):
        """Configure Gerrit base URL."""
        await cl.Message(content="""🌐 **Configure Gerrit Base URL**

Please enter the Gerrit server URL (e.g., https://review.opendev.org):

**Common Gerrit Servers:**
- OpenStack: https://review.opendev.org
- Eclipse: https://git.eclipse.org/r
- Android: https://android-review.googlesource.com

Enter the URL or type 'cancel' to go back.""").send()
    
    async def _configure_username_password(self, current_config: Dict[str, Any]):
        """Configure username and password authentication."""
        await cl.Message(content="""🔐 **Configure Username/Password Authentication**

Please enter your Gerrit credentials:

**Username**: Your Gerrit username
**Password**: Your Gerrit password or API token

**Note**: For OpenStack Gerrit, you can use your Launchpad account or create a Gerrit account.

Enter your username or type 'cancel' to go back.""").send()
    
    async def _configure_api_token(self, current_config: Dict[str, Any]):
        """Configure API token authentication."""
        await cl.Message(content="""🔑 **Configure API Token Authentication**

Please enter your Gerrit API token:

**How to get an API token:**
1. Go to your Gerrit server (e.g., https://review.opendev.org)
2. Sign in with your account
3. Go to Settings → HTTP Password
4. Generate a new password/token
5. Copy the token

**Note**: API tokens are more secure than passwords and don't expire.

Enter your API token or type 'cancel' to go back.""").send()
    
    async def _test_connection(self, current_config: Dict[str, Any]):
        """Test Gerrit connection."""
        try:
            from ..integrations.gerrit import GerritIntegration
            
            # Create Gerrit integration with current config
            gerrit = GerritIntegration(
                base_url=current_config.get('base_url'),
                username=current_config.get('username'),
                password=current_config.get('password'),
                api_token=current_config.get('api_token')
            )
            
            await cl.Message(content="🔍 **Testing Gerrit Connection...**\n\nPlease wait while I test the connection.").send()
            
            # Test authentication
            if gerrit.is_authenticated():
                success, error = gerrit.test_authentication()
                if success:
                    await cl.Message(content="✅ **Connection Successful!**\n\nYour Gerrit configuration is working correctly.").send()
                else:
                    await cl.Message(content=f"⚠️ **Connection Issue**\n\n{error}\n\nYou can still use Gerrit for public changes, but some features may be limited.").send()
            else:
                await cl.Message(content="ℹ️ **No Authentication Configured**\n\nYou can still use Gerrit for public changes, but authentication provides access to more features.").send()
            
        except Exception as e:
            logger.error(f"Error testing Gerrit connection: {e}")
            await cl.Message(content="❌ **Connection Test Failed**\n\nError testing connection. Please check your configuration.").send()
    
    async def _clear_configuration(self):
        """Clear Gerrit configuration."""
        cl.user_session.set(self.config_key, {})
        await cl.Message(content="🗑️ **Configuration Cleared**\n\nAll Gerrit settings have been reset.").send()
    
    async def handle_gerrit_input(self, input_text: str) -> bool:
        """Handle Gerrit configuration input.
        
        Args:
            input_text: User input text
            
        Returns:
            True if input was handled, False otherwise
        """
        try:
            current_config = cl.user_session.get(self.config_key, {})
            
            # Check if we're in a configuration flow
            if "base_url" in current_config.get("_pending", ""):
                await self._handle_base_url_input(input_text, current_config)
                return True
            elif "username" in current_config.get("_pending", ""):
                await self._handle_username_input(input_text, current_config)
                return True
            elif "password" in current_config.get("_pending", ""):
                await self._handle_password_input(input_text, current_config)
                return True
            elif "api_token" in current_config.get("_pending", ""):
                await self._handle_api_token_input(input_text, current_config)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error handling Gerrit input: {e}")
            return False
    
    async def _handle_base_url_input(self, input_text: str, current_config: Dict[str, Any]):
        """Handle base URL input."""
        if input_text.lower() == 'cancel':
            current_config.pop("_pending", None)
            cl.user_session.set(self.config_key, current_config)
            await self.show_config_ui()
        else:
            # Validate URL
            if input_text.startswith(('http://', 'https://')):
                current_config['base_url'] = input_text
                current_config.pop("_pending", None)
                cl.user_session.set(self.config_key, current_config)
                await cl.Message(content=f"✅ **Base URL Set**\n\nGerrit server: {input_text}").send()
                await self.show_config_ui()
            else:
                await cl.Message(content="❌ **Invalid URL**\n\nPlease enter a valid URL starting with http:// or https://").send()
    
    async def _handle_username_input(self, input_text: str, current_config: Dict[str, Any]):
        """Handle username input."""
        if input_text.lower() == 'cancel':
            current_config.pop("_pending", None)
            cl.user_session.set(self.config_key, current_config)
            await self.show_config_ui()
        else:
            current_config['username'] = input_text
            current_config['_pending'] = 'password'
            cl.user_session.set(self.config_key, current_config)
            await cl.Message(content="✅ **Username Set**\n\nNow enter your password or API token:").send()
    
    async def _handle_password_input(self, input_text: str, current_config: Dict[str, Any]):
        """Handle password input."""
        if input_text.lower() == 'cancel':
            current_config.pop("_pending", None)
            cl.user_session.set(self.config_key, current_config)
            await self.show_config_ui()
        else:
            current_config['password'] = input_text
            current_config.pop("_pending", None)
            cl.user_session.set(self.config_key, current_config)
            await cl.Message(content="✅ **Password Set**\n\nUsername/Password authentication configured.").send()
            await self.show_config_ui()
    
    async def _handle_api_token_input(self, input_text: str, current_config: Dict[str, Any]):
        """Handle API token input."""
        if input_text.lower() == 'cancel':
            current_config.pop("_pending", None)
            cl.user_session.set(self.config_key, current_config)
            await self.show_config_ui()
        else:
            current_config['api_token'] = input_text
            current_config.pop("_pending", None)
            cl.user_session.set(self.config_key, current_config)
            await cl.Message(content="✅ **API Token Set**\n\nToken-based authentication configured.").send()
            await self.show_config_ui()
    
    def get_gerrit_integration(self) -> 'GerritIntegration':
        """Get configured Gerrit integration instance.
        
        Returns:
            GerritIntegration instance with current configuration
        """
        from ..integrations.gerrit import GerritIntegration
        
        current_config = cl.user_session.get(self.config_key, {})
        
        return GerritIntegration(
            base_url=current_config.get('base_url'),
            username=current_config.get('username'),
            password=current_config.get('password'),
            api_token=current_config.get('api_token')
        )
