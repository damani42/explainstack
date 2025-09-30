"""ExplainStack Multi-Agent Application."""

import os
import logging
from typing import Optional

import chainlit as cl
import openai
from dotenv import load_dotenv

from .config import get_config
from .config import AgentConfig, AgentRouter
from .ui import AgentSelector

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

# Initialize multi-agent system
agent_config = AgentConfig(config)
agent_router = AgentRouter(agent_config)
agent_selector = AgentSelector(agent_router)

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
    welcome_message = """🤖 **Welcome to ExplainStack Multi-Agent System!**

I'm your AI assistant specialized in OpenStack development. I have multiple expert agents ready to help you:

**Available Agents:**
- 🧠 **Code Expert**: Explains Python code and OpenStack patterns
- 🔍 **Patch Reviewer**: Reviews Gerrit patches and suggests improvements  
- 🧹 **Import Cleaner**: Organizes imports according to OpenStack standards
- 💬 **Commit Writer**: Generates professional commit messages

**How to use:**
1. Send your code, patch, or question
2. I'll automatically suggest the best agent
3. Or specify an agent by typing its name

**Quick Start:**
- Send Python code → Code Expert
- Send a diff/patch → Patch Reviewer  
- Type "clean imports" + code → Import Cleaner
- Type "commit message" + diff → Commit Writer

Ready to help! What would you like to work on?"""
    
    await cl.Message(content=welcome_message).send()

@cl.on_message
async def main(message: cl.Message):
    """Main function with multi-agent system."""
    try:
        user_text = message.content
        logger.info(f"Received message: {user_text[:100]}...")
        
        # Input validation
        is_valid, validation_error = validate_input(user_text)
        if not is_valid:
            await cl.Message(content=f"❌ Error: {validation_error}").send()
            return
        
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

@cl.on_settings_update
async def setup_agent_selection(settings):
    """Handle agent selection settings."""
    logger.info(f"Settings updated: {settings}")
    # This can be used for future agent configuration