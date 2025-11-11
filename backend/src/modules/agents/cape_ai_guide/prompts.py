"""
Prompt Templates for CapeAI Guide Agent

Contains system and user prompt templates for OpenAI API integration.
Provides context-aware, role-based prompts for different user scenarios.
"""

from typing import Any, Dict, List, Optional


class PromptTemplates:
    """Manages prompt templates for the CapeAI Guide agent."""

    def get_system_prompt(
        self, user_level: Optional[str] = None, preferred_format: Optional[str] = None
    ) -> str:
        """Generate system prompt based on user characteristics."""

        base_prompt = """You are the CapeAI Guide, an intelligent assistant for the CapeControl platform. Your role is to help users navigate features, solve problems, and optimize their experience.

Key principles:
- Provide clear, actionable guidance
- Be helpful and encouraging
- Focus on practical solutions
- Reference specific features and workflows
- Suggest next steps when appropriate

Platform context:
- CapeControl is a comprehensive business automation platform
- Features include workflows, dashboards, integrations, user management
- Users range from beginners to advanced administrators
- The platform emphasizes ease of use and powerful automation capabilities"""

        # Adjust tone based on user level
        if user_level == "beginner":
            base_prompt += "\n\nFor this user: Use simple language, provide step-by-step instructions, explain terminology, and offer encouraging guidance for new users."
        elif user_level == "advanced":
            base_prompt += "\n\nFor this user: Provide concise, technical details, focus on advanced features and best practices, assume familiarity with platform concepts."
        else:
            base_prompt += "\n\nFor this user: Balance detail with clarity, provide context for recommendations, explain both basic and advanced options."

        # Adjust format based on preference
        if preferred_format == "steps":
            base_prompt += "\n\nResponse format: Structure your response as clear, numbered steps when providing instructions."
        elif preferred_format == "checklist":
            base_prompt += "\n\nResponse format: Use bullet points and checkboxes for actionable items when appropriate."
        elif preferred_format == "code":
            base_prompt += "\n\nResponse format: Include code examples, API calls, or configuration snippets when relevant."

        return base_prompt

    def get_user_prompt(
        self, query: str, context: Dict[str, Any], knowledge: List[Dict[str, Any]]
    ) -> str:
        """Generate user prompt with query, context, and knowledge base information."""

        prompt = f"User Question: {query}\n\n"

        # Add context information
        if context:
            prompt += "User Context:\n"
            if context.get("current_page"):
                prompt += f"- Current page: {context['current_page']}\n"
            if context.get("user_role"):
                prompt += f"- User role: {context['user_role']}\n"
            if context.get("features_used"):
                prompt += f"- Previously used features: {', '.join(context['features_used'])}\n"
            if context.get("query_intent"):
                prompt += f"- Query intent: {context['query_intent']}\n"
            prompt += "\n"

        # Add relevant knowledge base information
        if knowledge:
            prompt += "Relevant Documentation:\n"
            for i, doc in enumerate(knowledge[:3], 1):  # Limit to top 3 for context
                prompt += f"{i}. {doc['title']}\n"
                prompt += f"   {doc['content'][:200]}...\n"
                prompt += f"   URL: {doc['url']}\n\n"

        prompt += """Please provide a helpful response that:
1. Directly addresses the user's question
2. Uses the relevant documentation when applicable
3. Provides specific, actionable guidance
4. Suggests logical next steps
5. Maintains an encouraging and professional tone

If the question cannot be fully answered with available information, acknowledge this and suggest alternative resources or support channels."""

        return prompt

    def get_fallback_prompt(self, query: str, error: str) -> str:
        """Generate fallback prompt when primary processing fails."""
        return f"""I encountered an issue while processing your question: "{query}"

Error details: {error}

As a fallback, here are some general recommendations:
1. Check our help documentation at /docs
2. Try rephrasing your question with more specific terms
3. Contact our support team if you continue experiencing issues
4. Visit our community forum for user discussions and tips

I apologize for the inconvenience and appreciate your patience."""

    def get_suggestion_prompt(self, query: str, response: str) -> str:
        """Generate prompt for extracting helpful suggestions."""
        return f"""Based on this user query: "{query}"
And this response: "{response}"

Generate 3-5 helpful follow-up suggestions or related topics the user might find useful. 
Focus on:
- Logical next steps
- Related features to explore
- Best practices to consider
- Additional learning resources

Format as a simple list of actionable suggestions."""
