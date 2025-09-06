"""
LocalStorm Models Package - Production Fixed
==========================================

Database models for the LocalStorm application.
Fixed for production Heroku deployment.
"""

# app.models package: expose audit logs and main application models dynamically
import os
import importlib.util

from .audit_log import AuditEventType, AuditLog, AuditLogLevel

# Dynamically load main models from the sibling 'models.py' file
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
models_file = os.path.join(parent_dir, "models.py")
spec = importlib.util.spec_from_file_location("models_main", models_file)
models_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(models_main)

# Expose primary ORM classes
User = models_main.User
UserProfile = models_main.UserProfile
Conversation = models_main.Conversation
ConversationMessage = models_main.ConversationMessage
# Some tests expect Base to be importable from app.models
Base = getattr(models_main, "Base", None)

__all__ = [
    "AuditEventType",
    "AuditLog",
    "AuditLogLevel",
    "User",
    "UserProfile",
    "Conversation",
    "ConversationMessage",
    "Base",
]
