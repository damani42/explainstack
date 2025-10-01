import os
import logging
from typing import Optional

import chainlit as cl
import openai
from dotenv import load_dotenv

from .prompts import (
    explain_code_prompt,
    explain_patch_prompt,
    clean_imports_prompt,
    suggest_commit_message_prompt
)
from .config import get_config

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

# Initialization with error handling
try:
    setup_openai()
except RuntimeError as e:
    logger.critical(f"Critical configuration error: {e}")
    raise

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

def detect_intent(user_text: str) -> str:
    """Detect user intent with error handling."""
    try:
        text = user_text.lower()
        if text.startswith("diff ") or "---" in text:
            return "patch"
        if "nettoie" in text or "clean imports" in text:
            return "clean_imports"
        if any(keyword in text for keyword in ["commit message", "commit msg", "suggest commit", "git commit", "commit suggestion"]):
            return "commit_message"
        return "code"
    except Exception as e:
        logger.error(f"Error detecting intent: {e}")
        return "code"  # Default fallback

async def call_openai_api(prompt: str) -> tuple[bool, Optional[str], Optional[str]]:
    """Call OpenAI API with comprehensive error handling."""
    try:
        logger.info("Calling OpenAI API...")
        openai_config = config["openai"]
        response = openai.ChatCompletion.create(
            model=openai_config["model"],
            messages=[
                {"role": "system", "content": "You are an OpenStack expert who explains Python code clearly and professionally."},
                {"role": "user", "content": prompt}
            ],
            temperature=openai_config["temperature"],
            max_tokens=openai_config["max_tokens"],
        )
        
        explanation = response.choices[0].message["content"]
        logger.info("OpenAI API call successful")
        return True, explanation, None
        
    except openai.RateLimitError as e:
        error_msg = "Rate limit exceeded. Please try again in a few minutes."
        logger.warning(f"Rate limit error: {e}")
        return False, None, error_msg
        
    except openai.BadRequestError as e:
        error_msg = "Invalid request. Please check your code or patch."
        logger.warning(f"Invalid request error: {e}")
        return False, None, error_msg
        
    except openai.AuthenticationError as e:
        error_msg = "Authentication error. Please check your OpenAI API key."
        logger.error(f"Authentication error: {e}")
        return False, None, error_msg
        
    except openai.APIConnectionError as e:
        error_msg = "API connection error. Please check your internet connection."
        logger.error(f"API connection error: {e}")
        return False, None, error_msg
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"Unexpected error: {e}")
        return False, None, error_msg

@cl.on_message
async def main(message: cl.Message):
    """Main function with comprehensive error handling."""
    try:
        user_text = message.content
        logger.info(f"Received message: {user_text[:100]}...")
        
        # Input validation
        is_valid, validation_error = validate_input(user_text)
        if not is_valid:
            await cl.Message(content=f"❌ Error: {validation_error}").send()
            return
        
        # Intent detection
        intent = detect_intent(user_text)
        logger.info(f"Detected intent: {intent}")
        
        # Generate appropriate prompt
        try:
            if intent == "patch":
                prompt = explain_patch_prompt(user_text)
            elif intent == "clean_imports":
                prompt = clean_imports_prompt(user_text)
            elif intent == "commit_message":
                prompt = suggest_commit_message_prompt(user_text)
            else:
                prompt = explain_code_prompt(user_text)
        except Exception as e:
            logger.error(f"Error generating prompt: {e}")
            await cl.Message(content="❌ Error generating prompt. Please try again.").send()
            return
        
        # Call OpenAI API
        success, explanation, error_msg = await call_openai_api(prompt)
        
        if success and explanation:
            await cl.Message(content=explanation).send()
            logger.info("Response sent successfully")
        else:
            error_content = f"❌ {error_msg}"
            await cl.Message(content=error_content).send()
            logger.error(f"Failed to get response: {error_msg}")
            
    except Exception as e:
        logger.critical(f"Unexpected error in main: {e}")
        await cl.Message(content="❌ An unexpected error occurred. Please try again.").send()
