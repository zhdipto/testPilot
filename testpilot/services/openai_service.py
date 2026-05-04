"""Groq service integration for AI-powered commands."""

import os
from dotenv import load_dotenv
from openai import OpenAI
from testpilot.utils.console import print_error
import typer

# Load environment variables from .env
load_dotenv()


def get_client() -> OpenAI:
    """Initialize and return the Groq client."""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print_error("OPENAI_API_KEY is not set. Please add your Groq API key to the .env file.")
        raise typer.Exit(code=1)

    return OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )


def ask_ai(prompt: str) -> str:
    """
    Send a prompt to Groq and return the response text.
    Uses the model specified in testpilot.toml.
    """
    client = get_client()
    from testpilot.utils.config import load_config
    config = load_config()

    model_name = config.get("model", "llama-3.1-8b-instant")

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful expert developer assistant. Generate accurate pytest unit tests and explain Python code clearly."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
        )

        return response.choices[0].message.content or ""

    except Exception as e:
        print_error(f"Groq API Error: {e}")
        raise typer.Exit(code=1)