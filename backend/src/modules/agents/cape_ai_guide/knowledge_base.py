"""
Knowledge Base for CapeAI Guide Agent

Simulated knowledge base for searching documentation and help content.
In production, this would integrate with actual documentation systems.
"""

import asyncio
from typing import Any, Dict, List, Optional


class KnowledgeBase:
    """Simulated knowledge base for CapeControl documentation and help content."""

    def __init__(self):
        """Initialize the knowledge base with sample documentation."""
        self.documents = [
            {
                "id": "workflow-setup",
                "title": "Setting Up Automated Workflows",
                "content": "Learn how to create and configure automated workflows in CapeControl. Start by navigating to the Workflows section in your dashboard.",
                "url": "/docs/workflows/setup",
                "type": "doc",
                "keywords": ["workflow", "automation", "setup", "configure"],
                "relevance_score": 0.95,
            },
            {
                "id": "dashboard-customization",
                "title": "Customizing Your Dashboard",
                "content": "Personalize your CapeControl dashboard with widgets, layouts, and data views that matter most to your workflow.",
                "url": "/docs/dashboard/customization",
                "type": "doc",
                "keywords": ["dashboard", "customize", "widgets", "layout"],
                "relevance_score": 0.90,
            },
            {
                "id": "api-integration",
                "title": "API Integration Guide",
                "content": "Connect external systems to CapeControl using our RESTful API. Includes authentication, endpoints, and best practices.",
                "url": "/docs/api/integration",
                "type": "doc",
                "keywords": ["api", "integration", "rest", "authentication"],
                "relevance_score": 0.88,
            },
            {
                "id": "user-management",
                "title": "Managing Users and Permissions",
                "content": "Add team members, set roles, and configure permissions to control access to features and data.",
                "url": "/docs/users/management",
                "type": "doc",
                "keywords": ["users", "permissions", "roles", "team"],
                "relevance_score": 0.85,
            },
            {
                "id": "troubleshooting-guide",
                "title": "Common Issues and Solutions",
                "content": "Solutions to frequently encountered problems including login issues, data sync problems, and performance optimization.",
                "url": "/docs/troubleshooting",
                "type": "doc",
                "keywords": ["troubleshooting", "issues", "problems", "solutions"],
                "relevance_score": 0.80,
            },
            {
                "id": "workflow-tutorial",
                "title": "Workflow Tutorial: From Beginner to Pro",
                "content": "Step-by-step video tutorial covering everything from basic workflow creation to advanced automation techniques.",
                "url": "/tutorials/workflows/complete",
                "type": "tutorial",
                "keywords": ["workflow", "tutorial", "video", "beginner", "advanced"],
                "relevance_score": 0.92,
            },
            {
                "id": "getting-started",
                "title": "Getting Started with CapeControl",
                "content": "New to CapeControl? This guide walks you through setting up your account, configuring basic features, and your first tasks.",
                "url": "/docs/getting-started",
                "type": "doc",
                "keywords": ["getting started", "new user", "setup", "basics"],
                "relevance_score": 0.87,
            },
            {
                "id": "security-best-practices",
                "title": "Security and Best Practices",
                "content": "Protect your data and optimize your CapeControl usage with security recommendations and operational best practices.",
                "url": "/docs/security/best-practices",
                "type": "doc",
                "keywords": [
                    "security",
                    "best practices",
                    "protection",
                    "optimization",
                ],
                "relevance_score": 0.83,
            },
        ]

    async def search(
        self, query: str, context: Optional[Dict[str, Any]] = None, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search the knowledge base for relevant documents.

        Args:
            query: Search query from the user
            context: Additional context like current page, user role, etc.
            limit: Maximum number of results to return

        Returns:
            List of relevant documents sorted by relevance
        """

        # Simulate async operation
        await asyncio.sleep(0.1)

        query_lower = query.lower()
        results = []

        for doc in self.documents:
            # Calculate relevance score based on keyword matching
            score = 0.0

            # Check title match
            if any(word in doc["title"].lower() for word in query_lower.split()):
                score += 0.3

            # Check content match
            if any(word in doc["content"].lower() for word in query_lower.split()):
                score += 0.2

            # Check keyword match
            for keyword in doc["keywords"]:
                if keyword in query_lower:
                    score += 0.4

            # Boost score for exact keyword matches
            for word in query_lower.split():
                if word in doc["keywords"]:
                    score += 0.2

            # Context-based boosting
            if context:
                current_page = context.get("current_page", "")
                if "workflow" in current_page and "workflow" in doc["keywords"]:
                    score += 0.3
                elif "dashboard" in current_page and "dashboard" in doc["keywords"]:
                    score += 0.3
                elif "api" in current_page and "api" in doc["keywords"]:
                    score += 0.3

            if score > 0.1:  # Only include results with meaningful relevance
                doc_result = doc.copy()
                doc_result["search_score"] = score
                results.append(doc_result)

        # Sort by search score descending
        results.sort(key=lambda x: x["search_score"], reverse=True)

        return results[:limit]

    async def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by its ID."""
        await asyncio.sleep(0.05)  # Simulate async operation

        for doc in self.documents:
            if doc["id"] == doc_id:
                return doc.copy()

        return None

    async def get_popular_resources(
        self, category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get popular/recommended resources, optionally filtered by category."""
        await asyncio.sleep(0.1)  # Simulate async operation

        if category:
            category_lower = category.lower()
            filtered_docs = [
                doc
                for doc in self.documents
                if category_lower in doc["keywords"]
                or category_lower in doc["title"].lower()
            ]
            return sorted(
                filtered_docs, key=lambda x: x["relevance_score"], reverse=True
            )[:3]

        # Return top 5 most relevant documents overall
        return sorted(self.documents, key=lambda x: x["relevance_score"], reverse=True)[
            :5
        ]
