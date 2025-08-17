"""
LocalStorm Models Package - Production Fixed
==========================================

Database models for the LocalStorm application.
Fixed for production Heroku deployment.
"""

# Import audit log models
from .audit_log import AuditLog, AuditEventType, AuditLogLevel

# Import main models from models.py file
import sys
import os

# Add the parent directory to path to import from models.py
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
models_file = os.path.join(parent_dir, 'models.py')

if os.path.exists(models_file):
    import importlib.util
    spec = importlib.util.spec_from_file_location("models_main", models_file)
    if spec and spec.loader:
        models_main = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(models_main)
        
        # Export the main models
        User = models_main.User
        UserProfile = models_main.UserProfile
        Conversation = models_main.Conversation
        ConversationMessage = models_main.ConversationMessage

# Export all models
__all__ = [
    "AuditLog",
    "AuditEventType", 
    "AuditLogLevel",
    "User",
    "UserProfile",
    "Conversation",
    "ConversationMessage"
]

__all__ = [
    "AuditLog",
    "AuditEventType", 
    "AuditLogLevel"
]
