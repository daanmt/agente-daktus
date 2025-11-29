"""
Centralized Environment Loader

Loads .env file from project root.
Use this in any module that needs environment variables.
"""

from pathlib import Path
from dotenv import load_dotenv


def load_project_env():
    """
    Load .env file from project root.
    
    This function calculates the project root from the file location
    and loads the .env file from there.
    
    Safe to call multiple times (idempotent).
    """
    # Calculate project root: src/env_loader.py -> project root
    project_root = Path(__file__).resolve().parent.parent
    env_file = project_root / ".env"
    
    if env_file.exists():
        load_dotenv(env_file, override=True)
        return True
    else:
        # Fallback: try current working directory
        cwd_env = Path.cwd() / ".env"
        if cwd_env.exists():
            load_dotenv(cwd_env, override=True)
            return True
        else:
            # Last resort: default location
            load_dotenv(override=True)
            return False

