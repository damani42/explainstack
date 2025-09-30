"""ExplainStack Multi-Agent Application with Optional Authentication."""

import os
import logging
from typing import Optional

import chainlit as cl
import openai
from dotenv import load_dotenv

from .config import get_config
from .config import AgentConfig, AgentRouter
from .ui import AgentSelector, APIConfigUI
from .database import DatabaseManager
from .auth import AuthService, AuthMiddleware
from .user import UserService, UserPreferencesManager

# Configuration
config = get_config()

# Logging configuration
logging.basicConfig(
    level=getattr(logging, config["logging"]["level"]),
    format=config["logging"]["format"]
)
logger = logging.getLogger(__name__)

# OpenAI API configuration with error handling
def setup_openai():
    """Configure OpenAI API with error handling."""
    try:
        if "OPENAI_API_KEY" not in os.environ:
            load_dotenv()
        
        api_key = os.getenv("OPENAI_API_KEY", None)
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        
        openai.api_key = api_key
        logger.info("OpenAI API configured successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to configure OpenAI API: {e}")
        raise RuntimeError(f"Configuration error: {e}")

# Initialize with error handling
try:
    setup_openai()
except RuntimeError as e:
    logger.critical(f"Critical configuration error: {e}")
    raise

# Initialize database and authentication (optional)
db_manager = DatabaseManager()
auth_service = AuthService(db_manager)
auth_middleware = AuthMiddleware(auth_service)
user_service = UserService(auth_service)
preferences_manager = UserPreferencesManager(auth_service)

# Initialize multi-agent system
agent_config = AgentConfig(config)
agent_router = AgentRouter(agent_config)
agent_selector = AgentSelector(agent_router)
api_config_ui = APIConfigUI(auth_service, user_service)

def validate_input(user_text: str) -> tuple[bool, Optional[str]]:
    """Validate user input."""
    if not user_text or not user_text.strip():
        return False, "Message cannot be empty"
    
    min_length = config["validation"]["min_input_length"]
    max_length = config["validation"]["max_input_length"]
    
    if len(user_text) < min_length:
        return False, f"Message is too short (min {min_length} characters)"
    
    if len(user_text) > max_length:
        return False, f"Message is too long (max {max_length} characters)"
    
    return True, None

@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    # Check if user is authenticated
    session_id = cl.user_session.get("session_id")
    current_user = auth_middleware.get_current_user(session_id)
    
    if current_user:
        # User is authenticated
        user_info = auth_middleware.get_user_info(current_user)
        welcome_message = f"""🤖 **Welcome back to ExplainStack, {current_user.email}!**

I'm your AI assistant specialized in OpenStack development. You're logged in with your personal configuration.

**Your Profile:**
- 📧 Email: {current_user.email}
- 🎯 Default Agent: {preferences_manager.get_default_agent(current_user.user_id)}
- 🎨 Theme: {preferences_manager.get_theme(current_user.user_id)}

**Available Agents:**
- 🧠 **Code Expert**: Explains Python code and OpenStack patterns
- 🔍 **Patch Reviewer**: Reviews Gerrit patches and suggests improvements  
- 🧹 **Import Cleaner**: Organizes imports according to OpenStack standards
- 💬 **Commit Writer**: Generates professional commit messages

**Quick Commands:**
- Type `profile` to view your settings
- Type `api` to configure your API keys
- Type `logout` to sign out
- Send your code/patch for analysis

Ready to help! What would you like to work on?"""
    else:
        # User is not authenticated
        welcome_message = """🤖 **Welcome to ExplainStack Multi-Agent System!**

I'm your AI assistant specialized in OpenStack development. You can use me with or without an account.

**Available Agents:**
- 🧠 **Code Expert**: Explains Python code and OpenStack patterns
- 🔍 **Patch Reviewer**: Reviews Gerrit patches and suggests improvements  
- 🧹 **Import Cleaner**: Organizes imports according to OpenStack standards
- 💬 **Commit Writer**: Generates professional commit messages

**Quick Start:**
- Send Python code → Code Expert
- Send a diff/patch → Patch Reviewer  
- Type "clean imports" + code → Import Cleaner
- Type "commit message" + diff → Commit Writer

**Account Features:**
- Type `login` to sign in with your account
- Type `register` to create a new account
- Type `api` to configure personal API keys
- Personal preferences and session history

Ready to help! What would you like to work on?"""
    
    await cl.Message(content=welcome_message).send()

@cl.on_message
async def main(message: cl.Message):
    """Main function with multi-agent system and authentication."""
    try:
        user_text = message.content
        logger.info(f"Received message: {user_text[:100]}...")
        
        # Input validation
        is_valid, validation_error = validate_input(user_text)
        if not is_valid:
            await cl.Message(content=f"❌ Error: {validation_error}").send()
            return
        
        # Check for authentication commands
        if user_text.lower().strip() in ["login", "signin"]:
            await handle_login()
            return
        elif user_text.lower().strip() in ["register", "signup"]:
            await handle_register()
            return
        elif user_text.lower().strip() in ["logout", "signout"]:
            await handle_logout()
            return
        elif user_text.lower().strip() in ["profile", "settings"]:
            await handle_profile()
            return
        elif user_text.lower().strip() in ["api", "keys", "config"]:
            await handle_api_config()
            return
        
        # Get current user and configuration
        session_id = cl.user_session.get("session_id")
        current_user = auth_middleware.get_current_user(session_id)
        
        # Check for API configuration commands (only for authenticated users)
        if current_user and user_text.lower().startswith(("set ", "test ", "clear ")):
            handled = await api_config_ui.handle_api_command(current_user, user_text)
            if handled:
                return
        
        # Use user-specific configuration if authenticated
        if current_user:
            user_config = auth_middleware.get_user_config(current_user)
            # Update agent configuration with user preferences
            agent_config = AgentConfig(user_config)
            agent_router = AgentRouter(agent_config)
        
        # Check for agent selection commands
        selected_agent_id = agent_selector.parse_agent_selection(user_text)
        
        if selected_agent_id is None:
            # User cancelled or invalid selection
            if user_text.lower().strip() in ["cancel", "c"]:
                await cl.Message(content="❌ Operation cancelled.").send()
                return
            # Continue with normal processing
        
        # Route to appropriate agent
        success, response, error_msg = await agent_router.route_request(
            user_text, 
            selected_agent_id
        )
        
        if success and response:
            # Add agent info to response
            if selected_agent_id:
                agent_info = agent_router.get_available_agents().get(selected_agent_id)
                if agent_info:
                    response = f"🤖 **{agent_info['name']}**\n\n{response}"
            
            await cl.Message(content=response).send()
            logger.info("Response sent successfully")
        else:
            error_content = f"❌ {error_msg}"
            await cl.Message(content=error_content).send()
            logger.error(f"Failed to get response: {error_msg}")
            
    except Exception as e:
        logger.critical(f"Unexpected error in main: {e}")
        await cl.Message(content="❌ An unexpected error occurred. Please try again.").send()

async def handle_login():
    """Handle user login."""
    await cl.Message(content="""🔐 **Login to ExplainStack**

Please provide your credentials:
- Email: [Your email address]
- Password: [Your password]

Type your email and password separated by a space, or type 'cancel' to go back.

Example: `user@example.com mypassword`""").send()

async def handle_register():
    """Handle user registration."""
    await cl.Message(content="""📝 **Register for ExplainStack**

Create your account to get:
- Personal API keys and configuration
- Session history and analytics
- Custom preferences and themes

Please provide:
- Email: [Your email address]
- Password: [Your password - at least 8 characters]

Type your email and password separated by a space, or type 'cancel' to go back.

Example: `user@example.com mypassword`""").send()

async def handle_logout():
    """Handle user logout."""
    session_id = cl.user_session.get("session_id")
    if session_id:
        success, message = auth_service.logout_user(session_id)
        if success:
            cl.user_session.set("session_id", None)
            await cl.Message(content="✅ Successfully logged out. You can continue using ExplainStack without an account.").send()
        else:
            await cl.Message(content=f"❌ Logout failed: {message}").send()
    else:
        await cl.Message(content="ℹ️ You're not currently logged in.").send()

async def handle_profile():
    """Handle user profile display."""
    session_id = cl.user_session.get("session_id")
    current_user = auth_middleware.get_current_user(session_id)
    
    if current_user:
        user_info = auth_middleware.get_user_info(current_user)
        profile_text = f"""👤 **Your Profile**

**Account Information:**
- 📧 Email: {current_user.email}
- 🆔 User ID: {current_user.user_id}
- 📅 Member since: {current_user.created_at.strftime('%Y-%m-%d')}

**Preferences:**
- 🎯 Default Agent: {preferences_manager.get_default_agent(current_user.user_id)}
- 🎨 Theme: {preferences_manager.get_theme(current_user.user_id)}

**Quick Actions:**
- Type `settings` to update your preferences
- Type `api` to configure API keys
- Type `logout` to sign out
- Type `help` for more commands"""
        
        await cl.Message(content=profile_text).send()
    else:
        await cl.Message(content="ℹ️ You're not logged in. Type `login` to sign in or `register` to create an account.").send()

async def handle_api_config():
    """Handle API key configuration."""
    session_id = cl.user_session.get("session_id")
    current_user = auth_middleware.get_current_user(session_id)
    
    if current_user:
        await api_config_ui.show_api_configuration(current_user)
    else:
        await cl.Message(content="ℹ️ You need to be logged in to configure API keys. Type `login` to sign in or `register` to create an account.").send()

@cl.on_settings_update
async def setup_agent_selection(settings):
    """Handle agent selection settings."""
    logger.info(f"Settings updated: {settings}")
    # This can be used for future agent configuration