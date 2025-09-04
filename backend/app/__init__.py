# Ensure environment variables are loaded before any other imports
import os
from pathlib import Path

# Load environment variables if python-dotenv is installed
try:
    from dotenv import load_dotenv  # type: ignore[import]
except ImportError:
    # python-dotenv not available; define a no-op
    def load_dotenv(*args, **kwargs):
        pass


# Load .env from backend/.env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
