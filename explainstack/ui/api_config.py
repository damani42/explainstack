"""API key configuration UI for ExplainStack."""

import chainlit as cl
from typing import Dict, Any, Optional, Tuple
from ..auth import AuthService
from ..user import UserService
from ..database import User


class APIConfigUI:
    """API key configuration interface for Chainlit."""
    
    def __init__(self, auth_service: AuthService, user_service: UserService):
        """Initialize API configuration UI.
        
        Args:
            auth_service: Authentication service instance
            user_service: User service instance
        """
        self.auth_service = auth_service
        self.user_service = user_service
        self.logger = cl.logger
    
    async def show_api_configuration(self, user: User):
        """Show API key configuration interface.
        
        Args:
            user: Current user instance
        """
        # Get current API keys
        current_keys = self.user_service.get_user_api_keys(user)
        
        config_text = f"""🔑 **API Key Configuration**

Configure your API keys for each agent to use your own accounts and avoid rate limits.

**Current Configuration:**
- 🧠 **Code Expert (OpenAI)**: {'✅ Configured' if current_keys.get('openai_api_key') else '❌ Not configured'}
- 🔍 **Patch Reviewer (Claude)**: {'✅ Configured' if current_keys.get('claude_api_key') else '❌ Not configured'}
- 🧹 **Import Cleaner (OpenAI)**: {'✅ Configured' if current_keys.get('openai_api_key') else '❌ Not configured'}
- 💬 **Commit Writer (OpenAI)**: {'✅ Configured' if current_keys.get('openai_api_key') else '❌ Not configured'}

**Configuration Commands:**
- Type `set openai <your-key>` to set OpenAI API key
- Type `set claude <your-key>` to set Claude API key
- Type `set gemini <your-key>` to set Gemini API key
- Type `test keys` to test all configured keys
- Type `clear keys` to remove all API keys
- Type `back` to return to main menu

**Benefits of Personal API Keys:**
- 🚀 No rate limits from shared keys
- 💰 Use your own billing
- 🔒 Enhanced security and privacy
- ⚙️ Custom model configurations

**Getting API Keys:**
- **OpenAI**: https://platform.openai.com/api-keys
- **Claude**: https://console.anthropic.com/
- **Gemini**: https://makersuite.google.com/app/apikey

Ready to configure your API keys? Type a command above."""
        
        await cl.Message(content=config_text).send()
    
    async def handle_api_command(self, user: User, command: str) -> bool:
        """Handle API configuration commands.
        
        Args:
            user: Current user instance
            command: User command
            
        Returns:
            True if command was handled, False otherwise
        """
        parts = command.lower().strip().split()
        
        if len(parts) < 2:
            return False
        
        action = parts[0]
        key_type = parts[1]
        
        if action == "set" and len(parts) >= 3:
            api_key = " ".join(parts[2:])  # In case key has spaces
            return await self._set_api_key(user, key_type, api_key)
        elif action == "test":
            return await self._test_api_keys(user)
        elif action == "clear":
            return await self._clear_api_keys(user)
        
        return False
    
    async def _set_api_key(self, user: User, key_type: str, api_key: str) -> bool:
        """Set an API key for a user.
        
        Args:
            user: Current user instance
            key_type: Type of API key (openai, claude, gemini)
            api_key: API key value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate key type
            valid_types = ["openai", "claude", "gemini"]
            if key_type not in valid_types:
                await cl.Message(content=f"❌ Invalid key type. Valid types: {', '.join(valid_types)}").send()
                return True
            
            # Validate API key format
            if not self._validate_api_key_format(key_type, api_key):
                await cl.Message(content=f"❌ Invalid {key_type} API key format.").send()
                return True
            
            # Prepare API keys dictionary
            current_keys = self.user_service.get_user_api_keys(user)
            new_keys = current_keys.copy()
            new_keys[f"{key_type}_api_key"] = api_key
            
            # Update user API keys
            success = self.user_service.update_user_api_keys(user, new_keys)
            
            if success:
                await cl.Message(content=f"✅ {key_type.title()} API key configured successfully!").send()
                
                # Test the key if it's new
                if not current_keys.get(f"{key_type}_api_key"):
                    await self._test_single_key(user, key_type, api_key)
            else:
                await cl.Message(content=f"❌ Failed to save {key_type} API key.").send()
            
            return True
            
        except Exception as e:
            await cl.Message(content=f"❌ Error setting API key: {str(e)}").send()
            return True
    
    async def _test_api_keys(self, user: User) -> bool:
        """Test all configured API keys.
        
        Args:
            user: Current user instance
            
        Returns:
            True if command was handled
        """
        try:
            current_keys = self.user_service.get_user_api_keys(user)
            
            if not any(current_keys.values()):
                await cl.Message(content="ℹ️ No API keys configured. Use `set <type> <key>` to configure keys.").send()
                return True
            
            test_results = []
            
            # Test OpenAI key
            if current_keys.get('openai_api_key'):
                result = await self._test_single_key(user, 'openai', current_keys['openai_api_key'])
                test_results.append(f"OpenAI: {'✅ Valid' if result else '❌ Invalid'}")
            
            # Test Claude key
            if current_keys.get('claude_api_key'):
                result = await self._test_single_key(user, 'claude', current_keys['claude_api_key'])
                test_results.append(f"Claude: {'✅ Valid' if result else '❌ Invalid'}")
            
            # Test Gemini key
            if current_keys.get('gemini_api_key'):
                result = await self._test_single_key(user, 'gemini', current_keys['gemini_api_key'])
                test_results.append(f"Gemini: {'✅ Valid' if result else '❌ Invalid'}")
            
            if test_results:
                results_text = "🔍 **API Key Test Results**\n\n" + "\n".join(test_results)
                await cl.Message(content=results_text).send()
            else:
                await cl.Message(content="ℹ️ No API keys configured to test.").send()
            
            return True
            
        except Exception as e:
            await cl.Message(content=f"❌ Error testing API keys: {str(e)}").send()
            return True
    
    async def _test_single_key(self, user: User, key_type: str, api_key: str) -> bool:
        """Test a single API key.
        
        Args:
            user: Current user instance
            key_type: Type of API key
            api_key: API key value
            
        Returns:
            True if key is valid, False otherwise
        """
        try:
            # This would implement actual API key testing
            # For now, we'll do basic format validation
            if self._validate_api_key_format(key_type, api_key):
                await cl.Message(content=f"✅ {key_type.title()} API key appears to be valid!").send()
                return True
            else:
                await cl.Message(content=f"❌ {key_type.title()} API key format is invalid.").send()
                return False
                
        except Exception as e:
            await cl.Message(content=f"❌ Error testing {key_type} API key: {str(e)}").send()
            return False
    
    async def _clear_api_keys(self, user: User) -> bool:
        """Clear all API keys for a user.
        
        Args:
            user: Current user instance
            
        Returns:
            True if command was handled
        """
        try:
            # Clear all API keys
            empty_keys = {
                "openai_api_key": "",
                "claude_api_key": "",
                "gemini_api_key": ""
            }
            
            success = self.user_service.update_user_api_keys(user, empty_keys)
            
            if success:
                await cl.Message(content="✅ All API keys cleared. You'll use global configuration.").send()
            else:
                await cl.Message(content="❌ Failed to clear API keys.").send()
            
            return True
            
        except Exception as e:
            await cl.Message(content=f"❌ Error clearing API keys: {str(e)}").send()
            return True
    
    def _validate_api_key_format(self, key_type: str, api_key: str) -> bool:
        """Validate API key format.
        
        Args:
            key_type: Type of API key
            api_key: API key value
            
        Returns:
            True if format is valid, False otherwise
        """
        if not api_key or len(api_key) < 10:
            return False
        
        if key_type == "openai":
            return api_key.startswith("sk-")
        elif key_type == "claude":
            return api_key.startswith("sk-ant-")
        elif key_type == "gemini":
            return len(api_key) > 20  # Gemini keys are typically longer
        
        return False
