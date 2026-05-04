"""Configuration loader for TestPilot."""

from pathlib import Path
from typing import Any
import sys

# Use standard library tomllib if Python >= 3.11, else use tomli
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        # Fallback if tomli isn't installed for some reason
        tomllib = None

def load_config() -> dict[str, Any]:
    """Load configuration from testpilot.toml with fallback defaults."""
    config_path = Path("testpilot.toml")
    defaults = {
        "framework": "pytest",
        "model": "gpt-4o-mini",
        "output": "tests/"
    }
    
    if config_path.is_file() and tomllib:
        try:
            with config_path.open("rb") as f:
                user_config = tomllib.load(f)
                defaults.update(user_config)
        except Exception:
            pass
            
    return defaults
