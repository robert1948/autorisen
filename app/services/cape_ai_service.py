"""CapeAI Service"""
import random
from datetime import datetime
from typing import Any


class CapeAIService:
    def __init__(self):
        self.demo_responses = [
            "Welcome to CapeControl! I'm here to help you navigate the platform and get the most out of your business tools.",
            "I can help you with dashboard navigation, user management, analytics, and setting up your AI agents. What would you like to explore?",
            "Great question! Let me guide you through that feature. CapeControl offers comprehensive business automation tools.",
            "I notice you're exploring the platform. Here are some quick tips to get started with your business setup.",
            "That's an excellent use case! Let me show you how CapeControl can streamline that process for your business.",
            "I'm designed to provide contextual help based on where you are in the platform. Feel free to ask me anything!",
            "CapeControl integrates multiple AI providers and business tools. I can help you configure and optimize your setup.",
            "For that particular workflow, I'd recommend starting with the dashboard to get an overview of your current setup."
        ]
        
        self.contextual_responses = {
            "dashboard": "Looking at your dashboard, I can help you understand the metrics, set up widgets, or explain any data you're seeing.",
            "profile": "I can help you optimize your profile settings, configure preferences, or set up integrations.",
            "agents": "AI agents are powerful tools for automation. I can help you create, configure, or troubleshoot your agents.",
            "settings": "In settings, you can customize your experience. What specific configuration would you like help with?",
            "auth": "For authentication and security, I can guide you through setting up two-factor auth, managing sessions, or user permissions."
        }

    async def generate_response(self, message: str, context: dict[str, Any] = None) -> dict[str, Any]:
        """Generate a demo AI response"""
        
        # Simple keyword-based responses
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'start']):
            response = "Hello! 👋 Welcome to CapeControl. I'm your AI assistant, ready to help you navigate the platform and optimize your business workflows. What can I help you with today?"
        
        elif any(word in message_lower for word in ['help', 'guide', 'show']):
            response = "I'd be happy to help! 🚀 Here are some things I can assist you with:\n\n• Platform navigation and features\n• Setting up dashboards and analytics\n• Configuring AI agents\n• User management and permissions\n• Business workflow optimization\n\nWhat specifically would you like to explore?"
        
        elif any(word in message_lower for word in ['dashboard', 'analytics', 'metrics']):
            response = "📊 Great! The dashboard is your command center. I can help you:\n\n• Understand your key metrics\n• Set up custom widgets\n• Create automated reports\n• Configure alerts and notifications\n\nWould you like me to walk you through any specific dashboard feature?"
        
        elif any(word in message_lower for word in ['agent', 'ai', 'automation']):
            response = "🤖 AI agents are one of CapeControl's most powerful features! They can:\n\n• Automate repetitive tasks\n• Analyze data and generate insights\n• Handle customer interactions\n• Monitor and alert on business metrics\n\nWould you like to create your first agent or learn about existing ones?"
        
        elif any(word in message_lower for word in ['profile', 'settings', 'config']):
            response = "⚙️ Let's optimize your setup! I can help you:\n\n• Configure user preferences\n• Set up integrations\n• Manage security settings\n• Customize your workspace\n\nWhat aspect of your configuration would you like to adjust?"
        
        elif any(word in message_lower for word in ['thank', 'thanks']):
            response = "You're very welcome! 😊 I'm always here to help. Feel free to ask me anything as you explore CapeControl!"
        
        else:
            # Use a random demo response for other messages
            response = random.choice(self.demo_responses)
            
            # Add contextual information if available
            if context and 'path' in context:
                path = context['path'].lower()
                for key, ctx_response in self.contextual_responses.items():
                    if key in path:
                        response += f"\n\n💡 Since you're on the {key} page: {ctx_response}"
                        break
        
        return {
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "context_used": bool(context),
            "type": "demo_response"
        }

def get_cape_ai_service():
    return CapeAIService()
