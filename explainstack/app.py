"""ExplainStack Multi-Agent Application with Optional Authentication."""

import os
import time
import logging
from typing import Optional

import chainlit as cl
import openai
from dotenv import load_dotenv

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from explainstack.config import AgentConfig, AgentRouter
from explainstack.ui import AgentSelector, APIConfigUI
from explainstack.ui.gerrit_config import GerritConfigUI
from explainstack.database import DatabaseManager
from explainstack.auth import AuthService, AuthMiddleware
from explainstack.user import UserService, UserPreferencesManager
from explainstack.utils import FileHandler
from explainstack.integrations import GerritIntegration
from explainstack.analytics import AnalyticsManager

# Configuration - using environment variables for API keys
config_data = {
    "backends": {
        "code_expert": {
            "type": "openai",
            "config": {
                "api_key": os.getenv("OPENAI_API_KEY", "demo-key"),
                "model": "gpt-4",
                "temperature": 0.3,
                "max_tokens": 2000
            }
        },
        "patch_reviewer": {
            "type": "claude",
            "config": {
                "api_key": os.getenv("ANTHROPIC_API_KEY", "demo-key"),
                "model": "claude-3-sonnet-20240229",
                "temperature": 0.2,
                "max_tokens": 3000
            }
        },
        "import_cleaner": {
            "type": "openai",
            "config": {
                "api_key": os.getenv("OPENAI_API_KEY", "demo-key"),
                "model": "gpt-3.5-turbo",
                "temperature": 0.1,
                "max_tokens": 1000
            }
        },
        "commit_writer": {
            "type": "openai",
            "config": {
                "api_key": os.getenv("OPENAI_API_KEY", "demo-key"),
                "model": "gpt-4",
                "temperature": 0.3,
                "max_tokens": 1500
            }
        },
        "security_expert": {
            "type": "claude",
            "config": {
                "api_key": os.getenv("ANTHROPIC_API_KEY", "demo-key"),
                "model": "claude-3-sonnet-20240229",
                "temperature": 0.1,
                "max_tokens": 3000
            }
        },
        "performance_expert": {
            "type": "openai",
            "config": {
                "api_key": os.getenv("OPENAI_API_KEY", "demo-key"),
                "model": "gpt-4",
                "temperature": 0.2,
                "max_tokens": 2500
            }
        }
    },
    "validation": {
        "max_input_length": 100000,
        "min_input_length": 1,
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    }
}

# Logging configuration
logging.basicConfig(
    level=getattr(logging, config_data["logging"]["level"]),
    format=config_data["logging"]["format"]
)
logger = logging.getLogger(__name__)

# OpenAI API configuration with error handling
def setup_openai():
    """Configure OpenAI API with error handling."""
    try:
        if "OPENAI_API_KEY" not in os.environ:
            load_dotenv()

        api_key = os.getenv("OPENAI_API_KEY", None)
        if not api_key or api_key == "demo-key":
            logger.warning("OpenAI API key not set - running in demo mode")
            return False
        
        openai.api_key = api_key
        logger.info("OpenAI API configured successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to configure OpenAI API: {e}")
        return False

# Initialize with error handling
demo_mode = not setup_openai()
if demo_mode:
    logger.info("Running in demo mode - some features may be limited")

# Initialize database and authentication (optional)
db_manager = DatabaseManager()
auth_service = AuthService(db_manager)
auth_middleware = AuthMiddleware(auth_service)
user_service = UserService(auth_service)
preferences_manager = UserPreferencesManager(auth_service)

# Initialize multi-agent system
agent_config = AgentConfig(config_data)
agent_router = AgentRouter(agent_config)
agent_selector = AgentSelector(agent_router)
api_config_ui = APIConfigUI(auth_service, user_service)
gerrit_config_ui = GerritConfigUI()
file_handler = FileHandler()
# Gerrit integration will be initialized dynamically with user config
analytics_manager = AnalyticsManager()

def validate_input(user_text: str) -> tuple[bool, Optional[str]]:
    """Validate user input."""
    if not user_text or not user_text.strip():
        return False, "Message cannot be empty"
    
    min_length = config_data["validation"]["min_input_length"]
    max_length = config_data["validation"]["max_input_length"]
    
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
- 🔒 **Security Expert**: Analyzes code for vulnerabilities and security issues
- ⚡ **Performance Expert**: Optimizes code for better performance and scalability

**Quick Start:**
- Send Python code → Code Expert
- Send a diff/patch → Patch Reviewer  
- Type "clean imports" + code → Import Cleaner
- Type "commit message" + diff → Commit Writer
- Type "security" + code → Security Expert
- Type "performance" + code → Performance Expert
- 📁 **Upload files** (.py, .diff, .patch) for analysis
- 🔗 **Paste Gerrit URLs** for automatic analysis

**Account Features:**
- Type `login` to sign in with your account
- Type `register` to create a new account
- Type `api` to configure personal API keys
- Type `gerrit` to configure Gerrit authentication
- Type `analytics` to view usage statistics
- Personal preferences and session history

Ready to help! What would you like to work on?"""
    
    await cl.Message(content=welcome_message).send()

async def handle_file_upload(elements):
    """Handle uploaded files."""
    try:
        for element in elements:
            if hasattr(element, 'content') and hasattr(element, 'name'):
                # Save uploaded file
                success, file_path, error_msg = file_handler.save_uploaded_file(
                    element.content, element.name
                )
                
                if not success:
                    await cl.Message(content=f"❌ Error uploading file: {error_msg}").send()
                    continue
                
                # Process file for analysis
                success, file_info, error_msg = file_handler.process_file_for_analysis(file_path)
                if not success:
                    await cl.Message(content=f"❌ Error processing file: {error_msg}").send()
                    continue
                
                # Display file info
                file_info_msg = f"""📁 **File Uploaded Successfully!**

**File:** {file_info['filename']}
**Size:** {file_info['size']} bytes
**Lines:** {file_info['lines']}
**Type:** {file_info['extension']}

**Content Preview:**
```python
{file_info['content'][:500]}{'...' if len(file_info['content']) > 500 else ''}
```

**What would you like to do with this file?**
- Type `explain` to analyze the code
- Type `security` to check for vulnerabilities  
- Type `review` to review the code
- Type `clean imports` to organize imports
- Type `commit message` to generate a commit message

Or just ask me anything about this code!"""
                
                await cl.Message(content=file_info_msg).send()
                
                # Store file content in session for further analysis
                cl.user_session.set("uploaded_file", file_info)
                logger.info(f"File uploaded and processed: {file_info['filename']}")
                
    except Exception as e:
        logger.error(f"Error handling file upload: {e}")
        await cl.Message(content="❌ Error processing uploaded file. Please try again.").send()

async def handle_gerrit_url(url: str):
    """Handle Gerrit URL analysis."""
    try:
        # Show loading message
        await cl.Message(content="🔍 **Analyzing Gerrit URL...**\n\nPlease wait while I fetch the change information.").send()
        
        # Get configured Gerrit integration
        configured_gerrit = gerrit_config_ui.get_gerrit_integration()
        
        # Analyze Gerrit URL
        success, analysis_result, error_msg = configured_gerrit.analyze_gerrit_url(url)
        
        if not success:
            # Check if it's an authentication error
            if "Authentication required" in error_msg:
                await cl.Message(content=f"""❌ **Authentication Required**

{error_msg}

**To fix this:**
1. Type `gerrit` to configure Gerrit authentication
2. Set up your Gerrit credentials
3. Try the URL again

**Note**: Some Gerrit changes are public and don't require authentication, but others do.""").send()
            else:
                await cl.Message(content=f"❌ **Error analyzing Gerrit URL:**\n\n{error_msg}").send()
            return
        
        # Format and display analysis
        formatted_analysis = configured_gerrit.format_gerrit_analysis(analysis_result)
        await cl.Message(content=formatted_analysis).send()
        
        # Store Gerrit data in session for further analysis
        cl.user_session.set("gerrit_analysis", analysis_result)
        logger.info(f"Gerrit URL analyzed successfully: {url}")
        
    except Exception as e:
        logger.error(f"Error handling Gerrit URL {url}: {e}")
        await cl.Message(content="❌ Error analyzing Gerrit URL. Please try again.").send()

async def handle_analytics():
    """Handle analytics dashboard request."""
    try:
        # Get current user
        session_id = cl.user_session.get("session_id")
        current_user = auth_middleware.get_current_user(session_id)
        
        if not current_user:
            await cl.Message(content="❌ **Analytics Dashboard**\n\nPlease log in to view analytics.").send()
            return
        
        # Get analytics data
        dashboard_data = analytics_manager.get_dashboard_data(current_user.id, hours=24)
        
        # Generate analytics report
        report = analytics_manager.generate_analytics_report(hours=24)
        
        await cl.Message(content=report).send()
        logger.info(f"Analytics dashboard displayed for user {current_user.id}")
        
    except Exception as e:
        logger.error(f"Error handling analytics request: {e}")
        await cl.Message(content="❌ Error loading analytics. Please try again.").send()

async def handle_gerrit_config():
    """Handle Gerrit configuration."""
    try:
        await gerrit_config_ui.show_config_ui()
    except Exception as e:
        logger.error(f"Error handling Gerrit config: {e}")
        await cl.Message(content="❌ Error loading Gerrit configuration. Please try again.").send()

@cl.on_message
async def main(message: cl.Message):
    """Main function with multi-agent system and authentication."""
    try:
        # Handle file uploads
        if message.elements:
            await handle_file_upload(message.elements)
            return
        
        user_text = message.content
        logger.info(f"Received message: {user_text[:100]}...")
        
        # Check if user has uploaded a file and wants to analyze it
        uploaded_file = cl.user_session.get("uploaded_file")
        if uploaded_file and user_text.lower().strip() in ["explain", "security", "review", "clean imports", "commit message"]:
            # Use uploaded file content for analysis
            user_text = f"{user_text}\n\n```python\n{uploaded_file['content']}\n```"
            logger.info("Using uploaded file content for analysis")
        
        # Check if user has Gerrit analysis and wants to analyze it
        gerrit_analysis = cl.user_session.get("gerrit_analysis")
        if gerrit_analysis and user_text.lower().strip() in ["review", "security", "performance", "commit message"]:
            # Use Gerrit diff content for analysis
            diff_content = gerrit_analysis.get('diff_content', '')
            if diff_content:
                user_text = f"{user_text}\n\n```diff\n{diff_content}\n```"
                logger.info("Using Gerrit diff content for analysis")
        
        # Check if user provided a Gerrit URL
        gerrit_integration = get_gerrit_integration()
        if gerrit_integration.is_gerrit_url(user_text.strip()):
            await handle_gerrit_url(user_text.strip())
            return
        
        # Input validation
        is_valid, validation_error = validate_input(user_text)
        if not is_valid:
            await cl.Message(content=f"❌ Error: {validation_error}").send()
            return
        
        # Check for authentication commands first
        logger.info(f"Checking command for: '{user_text.lower().strip()}'")
        if user_text.lower().strip() in ["login", "signin"]:
            logger.info("Detected login command")
            await handle_login()
            return
        elif user_text.lower().strip() in ["register", "signup"]:
            logger.info("Detected register command")
            await handle_register()
            return
        elif user_text.lower().strip() in ["logout", "signout"]:
            logger.info("Detected logout command")
            await handle_logout()
            return
        elif user_text.lower().strip() in ["profile", "settings"]:
            logger.info("Detected profile command")
            await handle_profile()
            return
        elif user_text.lower().strip() in ["api", "keys", "config", "set openai", "set claude", "set anthropic", "configure openai", "configure claude"]:
            logger.info("Detected api command")
            await handle_api_config()
            return
        elif user_text.lower().strip() in ["analytics", "metrics", "stats"]:
            logger.info("Detected analytics command")
            await handle_analytics()
            return
        elif user_text.lower().strip() in ["gerrit", "gerrit config", "gerrit settings"]:
            logger.info("Detected gerrit command")
            await handle_gerrit_config()
            return
        
        # Get current user and configuration
        session_id = cl.user_session.get("session_id")
        current_user = auth_middleware.get_current_user(session_id)
        
        # Check for API configuration commands FIRST (only for authenticated users)
        user_logged_in = cl.user_session.get("user_logged_in", False)
        user_email = cl.user_session.get("user_email", "")
        
        if user_logged_in and user_email and user_text.lower().startswith(("set ", "test ", "clear ")):
            # Get the real user object from database
            try:
                real_user = auth_service.db.get_user_by_email(user_email)
                if real_user:
                    handled = await api_config_ui.handle_api_command(real_user, user_text)
                    if handled:
                        return
                else:
                    await cl.Message(content="❌ User not found in database. Please login again.").send()
                    return
            except Exception as e:
                logger.error(f"Failed to get user for API config: {e}")
                await cl.Message(content="❌ Error accessing user data. Please try again.").send()
                return
        
        # Check for authentication responses AFTER API commands
        if await handle_auth_responses(user_text):
            return
        
        # Check for Gerrit configuration responses (after command detection)
        if await gerrit_config_ui.handle_gerrit_input(user_text):
            return
        
        # Use user-specific configuration if authenticated, otherwise use default
        if user_logged_in and user_email:
            # Create dynamic config with user's API keys from database
            dynamic_config = create_dynamic_config(config_data, user_email)
            agent_config = AgentConfig(dynamic_config)
        else:
            # Use default configuration for non-authenticated users
            agent_config = AgentConfig(config_data)
        
        # Create agent router with the appropriate configuration
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
        start_time = time.time()
        success, response, error_msg = await agent_router.route_request(
            user_text, 
            selected_agent_id
        )
        response_time = time.time() - start_time
        
        # Track analytics
        session_id = cl.user_session.get("session_id")
        current_user = auth_middleware.get_current_user(session_id)
        user_id = current_user.id if current_user else "anonymous"
        
        # Track agent usage
        agent_id = selected_agent_id or agent_router.get_auto_suggestion(user_text)
        analytics_manager.track_agent_usage(
            agent_id=agent_id,
            user_id=user_id,
            tokens_used=len(user_text) + len(response) if response else 0,
            cost=0.0,  # TODO: Calculate actual cost
            response_time=response_time,
            success=success
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
    # Check if user is already logged in
    user_logged_in = cl.user_session.get("user_logged_in", False)
    user_email = cl.user_session.get("user_email", "")
    
    if user_logged_in and user_email:
        # User is already logged in
        await cl.Message(content=f"""✅ **Already Logged In**

You are currently logged in as: **{user_email}**

**What would you like to do?**
1. **Stay logged in** - Continue with current session
2. **View profile** - See your account information
3. **Logout** - Sign out and login with different account
4. **Switch account** - Login with different credentials

Type the number of your choice (1-4), or type 'cancel' to go back.""").send()
        
        # Set auth state to handle login options
        cl.user_session.set("auth_state", "login_options")
        return
    
    # User is not logged in, proceed with normal login
    cl.user_session.set("auth_state", "login")
    
    await cl.Message(content="""🔐 **Login to ExplainStack**

Please provide your credentials:
- Email: [Your email address]
- Password: [Your password]

Type your email and password separated by a space, or type 'cancel' to go back.

Example: `user@example.com mypassword`""").send()

def get_gerrit_integration() -> GerritIntegration:
    """Get Gerrit integration with user configuration.
    
    Returns:
        Configured GerritIntegration instance
    """
    # Get Gerrit configuration from session
    gerrit_config = cl.user_session.get("gerrit_config", {})
    
    base_url = gerrit_config.get("base_url", "https://review.opendev.org")
    username = gerrit_config.get("username", "")
    password = gerrit_config.get("password", "")
    api_token = gerrit_config.get("api_token", "")
    
    return GerritIntegration(
        base_url=base_url,
        username=username,
        password=password,
        api_token=api_token
    )

def create_dynamic_config(base_config: dict, user_email: str = None) -> dict:
    """Create dynamic configuration using user's API keys from database.
    
    Args:
        base_config: Base configuration dictionary
        user_email: User email to get API keys from database
        
    Returns:
        Updated configuration with user's API keys
    """
    # Create a copy of the base config
    dynamic_config = base_config.copy()
    
    # If no user email, return base config
    if not user_email:
        return dynamic_config
    
    try:
        # Get user from database
        user = auth_service.db.get_user_by_email(user_email)
        if not user:
            return dynamic_config
        
        # Get user's API keys from database
        user_keys = user_service.get_user_api_keys(user)
        
        # Update OpenAI backends with user's key if available
        if user_keys.get("openai_api_key"):
            for agent_name, agent_config in dynamic_config["backends"].items():
                if agent_config["type"] == "openai":
                    agent_config["config"]["api_key"] = user_keys["openai_api_key"]
        
        # Update Claude backends with user's key if available
        if user_keys.get("claude_api_key"):
            for agent_name, agent_config in dynamic_config["backends"].items():
                if agent_config["type"] == "claude":
                    agent_config["config"]["api_key"] = user_keys["claude_api_key"]
        
        # Update Gemini backends with user's key if available
        if user_keys.get("gemini_api_key"):
            for agent_name, agent_config in dynamic_config["backends"].items():
                if agent_config["type"] == "gemini":
                    agent_config["config"]["api_key"] = user_keys["gemini_api_key"]
        
    except Exception as e:
        logger.error(f"Failed to load user API keys: {e}")
    
    return dynamic_config

async def handle_auth_responses(user_text: str) -> bool:
    """Handle authentication responses.
    
    Args:
        user_text: User input text
        
    Returns:
        True if input was handled, False otherwise
    """
    try:
        # Check if we're in an authentication flow
        auth_state = cl.user_session.get("auth_state")
        
        if auth_state == "register":
            # Handle registration response
            if user_text.lower() == "cancel":
                cl.user_session.set("auth_state", None)
                await cl.Message(content="❌ Registration cancelled.").send()
                return True
            
            # Process registration (email and password)
            parts = user_text.strip().split()
            if len(parts) >= 2:
                email = parts[0]
                password = " ".join(parts[1:])
                
                # Validate email format
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, email):
                    await cl.Message(content="❌ **Invalid email format!**\n\nPlease provide a valid email address.\n\nExample: `user@example.com mypassword`").send()
                    return True
                
                # Validate password strength
                if len(password) < 8:
                    await cl.Message(content="❌ **Password too short!**\n\nPassword must be at least 8 characters long.\n\nExample: `user@example.com mypassword123`").send()
                    return True
                
                if not re.search(r'[A-Za-z]', password):
                    await cl.Message(content="❌ **Password too weak!**\n\nPassword must contain at least one letter.\n\nExample: `user@example.com mypassword123`").send()
                    return True
                
                if not re.search(r'[0-9]', password):
                    await cl.Message(content="❌ **Password too weak!**\n\nPassword must contain at least one number.\n\nExample: `user@example.com mypassword123`").send()
                    return True
                
                # Create user in database
                try:
                    # Register user using AuthService
                    success, message, user = auth_service.register_user(email, password)
                    if not success:
                        await cl.Message(content=f"❌ Failed to create account: {message}").send()
                        return True
                    
                    # Default preferences are created automatically by register_user
                    
                    await cl.Message(content=f"""✅ **Registration Successful!**

Welcome to ExplainStack! Your account has been created:
- Email: {email}
- Status: Active
- Password: {'*' * len(password)} (hidden for security)

You can now configure your API keys by typing `api` or `config`.""").send()
                    
                    # Save user session
                    cl.user_session.set("user_email", email)
                    cl.user_session.set("user_logged_in", True)
                    cl.user_session.set("auth_state", None)
                    return True
                    
                except Exception as e:
                    await cl.Message(content=f"❌ Failed to create account: {str(e)}").send()
                    return True
            else:
                await cl.Message(content="❌ Please provide both email and password separated by a space.\n\nExample: `user@example.com mypassword`").send()
                return True
        
        elif auth_state == "login_options":
            # Handle login options for already logged in user
            if user_text.lower() == "cancel":
                cl.user_session.set("auth_state", None)
                await cl.Message(content="❌ Login options cancelled.").send()
                return True
            
            if user_text.strip() == "1":
                # Stay logged in
                cl.user_session.set("auth_state", None)
                await cl.Message(content="✅ **Continuing with current session**\n\nYou're all set! You can now use all features with your current account.").send()
                return True
            elif user_text.strip() == "2":
                # View profile
                cl.user_session.set("auth_state", None)
                await handle_profile()
                return True
            elif user_text.strip() == "3":
                # Logout
                cl.user_session.set("auth_state", None)
                await handle_logout()
                return True
            elif user_text.strip() == "4":
                # Switch account - proceed with login
                cl.user_session.set("auth_state", "login")
                await cl.Message(content="""🔐 **Switch Account**

Please provide your new credentials:
- Email: [Your email address]
- Password: [Your password]

Type your email and password separated by a space, or type 'cancel' to go back.

Example: `user@example.com mypassword`""").send()
                return True
            else:
                await cl.Message(content="❌ Please select a valid option (1-4) or type 'cancel'.").send()
                return True
        
        elif auth_state == "login":
            # Handle login response
            if user_text.lower() == "cancel":
                cl.user_session.set("auth_state", None)
                await cl.Message(content="❌ Login cancelled.").send()
                return True
            
            # Process login (email and password)
            parts = user_text.strip().split()
            if len(parts) >= 2:
                email = parts[0]
                password = " ".join(parts[1:])
                
                # Validate email format
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, email):
                    await cl.Message(content="❌ **Invalid email format!**\n\nPlease provide a valid email address.\n\nExample: `user@example.com mypassword`").send()
                    return True
                
                # Validate credentials against database
                try:
                    user = auth_service.db.get_user_by_email(email)
                    if not user:
                        await cl.Message(content="❌ **Login Failed!**\n\nAccount not found. Please check your email or register a new account.").send()
                        return True
                    
                    if not user.verify_password(password):
                        await cl.Message(content="❌ **Login Failed!**\n\nInvalid password. Please try again.").send()
                        return True
                    
                    await cl.Message(content=f"""✅ **Login Successful!**

Welcome back to ExplainStack!
- Email: {email}
- Status: Logged in

You can now access your personal settings and API configurations.""").send()
                    
                    # Save user session
                    cl.user_session.set("user_email", email)
                    cl.user_session.set("user_logged_in", True)
                    cl.user_session.set("auth_state", None)
                    return True
                    
                except Exception as e:
                    await cl.Message(content=f"❌ Login failed: {str(e)}").send()
                    return True
            else:
                await cl.Message(content="❌ Please provide both email and password separated by a space.\n\nExample: `user@example.com mypassword`").send()
                return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error handling auth response: {e}")
        return False

async def handle_register():
    """Handle user registration."""
    # Set auth state to register
    cl.user_session.set("auth_state", "register")
    
    await cl.Message(content="""📝 **Register for ExplainStack**

Create your account to get:
- Personal API keys and configuration
- Session history and analytics
- Custom preferences and themes

**Requirements:**
- Email: Valid email address (e.g., user@example.com)
- Password: At least 8 characters with letters and numbers

Type your email and password separated by a space, or type 'cancel' to go back.

Example: `user@example.com mypassword123`""").send()

async def handle_logout():
    """Handle user logout."""
    user_logged_in = cl.user_session.get("user_logged_in", False)
    user_email = cl.user_session.get("user_email", "")
    
    if user_logged_in and user_email:
        # Clear user session
        cl.user_session.set("user_logged_in", False)
        cl.user_session.set("user_email", "")
        cl.user_session.set("session_id", None)
        await cl.Message(content=f"✅ Successfully logged out ({user_email}). You can continue using ExplainStack without an account.").send()
    else:
        await cl.Message(content="ℹ️ You're not currently logged in.").send()

async def handle_profile():
    """Handle user profile display."""
    user_logged_in = cl.user_session.get("user_logged_in", False)
    user_email = cl.user_session.get("user_email", "")
    
    if user_logged_in and user_email:
        profile_text = f"""👤 **Your Profile**

**Account Information:**
- 📧 Email: {user_email}
- 🆔 User ID: user_{user_email.replace('@', '_').replace('.', '_')}
- 📅 Member since: Today

**Preferences:**
- 🎯 Default Agent: Auto-selected
- 🎨 Theme: Default

**Quick Actions:**
- Type `api` to configure API keys
- Type `logout` to sign out
- Type `help` for more commands"""
        
        await cl.Message(content=profile_text).send()
    else:
        await cl.Message(content="ℹ️ You're not logged in. Type `login` to sign in or `register` to create an account.").send()

async def handle_api_config():
    """Handle API key configuration."""
    # Check if user is logged in using our session management
    user_logged_in = cl.user_session.get("user_logged_in", False)
    user_email = cl.user_session.get("user_email", "")
    
    if user_logged_in and user_email:
        # Get the real user object from database
        try:
            real_user = auth_service.db.get_user_by_email(user_email)
            if real_user:
                await api_config_ui.show_api_configuration(real_user)
            else:
                await cl.Message(content="❌ User not found in database. Please login again.").send()
        except Exception as e:
            logger.error(f"Failed to get user for API config: {e}")
            await cl.Message(content="❌ Error accessing user data. Please try again.").send()
    else:
        await cl.Message(content="ℹ️ You need to be logged in to configure API keys. Type `login` to sign in or `register` to create an account.").send()

@cl.on_settings_update
async def setup_agent_selection(settings):
    """Handle agent selection settings."""
    logger.info(f"Settings updated: {settings}")
    # This can be used for future agent configuration
