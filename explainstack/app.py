import os

import chainlit as cl
import openai
from dotenv import load_dotenv

from .prompts import (
    explain_code_prompt,
    explain_patch_prompt,
    clean_imports_prompt
)

if "OPENAI_API_KEY" not in os.environ:
    load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY", None)
if not openai.api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is not set. Define it in your environment or in a"
        " .env file.")

def detect_intent(user_text: str) -> str:
    text = user_text.lower()
    if text.startswith("diff ") or "---" in text:
        return "patch"
    if "nettoie" in text or "clean imports" in text:
        return "clean_imports"
    return "code"

@cl.on_message
async def main(message: cl.Message):
    user_text = message.content
    intent = detect_intent(user_text)

    if intent == "patch":
        prompt = explain_patch_prompt(user_text)
    elif intent == "clean_imports":
        prompt = clean_imports_prompt(user_text)
    else:
        prompt = explain_code_prompt(user_text)

    content = "You are an OpenStack expert who explains Python code clearly and professionally."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": content},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
    )
    explanation = response.choices[0].message["content"]
    await cl.Message(content=explanation).send()
