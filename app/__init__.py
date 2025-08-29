# Ensure environment variables are loaded before any other imports
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from backend/.env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
