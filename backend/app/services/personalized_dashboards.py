"""
Task 2.2.4: Personalized Dashboards
Intelligent, context-aware user interfaces with role-specific widgets and adaptive layouts.
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from collections import defaultdict, Counter
import uuid

logger = logging.getLogger(__name__)

class DashboardRole(Enum):
    """User roles for dashboard personalization"""
    DEVELOPER = "developer"
    BUSINESS_USER = "business_user"
    ANALYST = "analyst"
    MANAGER = "manager"
    ADMIN = "admin"
    CONTENT_CREATOR = "content_creator"
    STUDENT = "student"
    RESEARCHER = "researcher"

class LayoutType(Enum):
    """Dashboard layout types"""
    GRID = "grid"           # Traditional grid layout
    KANBAN = "kanban"       # Kanban-style columns
    TIMELINE = "timeline"   # Timeline-based layout
    FOCUS = "focus"         # Single-focus minimal layout
    COMPACT = "compact"     # Dense information display
    VISUAL = "visual"       # Chart and graph heavy

class WidgetType(Enum):
    """Available widget types"""
    AI_CHAT = "ai_chat"
    CONVERSATION_LIST = "conversation_list"
    ANALYTICS_CHART = "analytics_chart"
    QUICK_ACTIONS = "quick_actions"
    RECENT_ACTIVITY = "recent_activity"
    PERFORMANCE_METRICS = "performance_metrics"
    USER_PROFILE = "user_profile"
    NOTIFICATIONS = "notifications"
    FAVORITES = "favorites"
    SEARCH = "search"
    CALENDAR = "calendar"
    TASKS = "tasks"
    NOTES = "notes"
    WEATHER = "weather"
    NEWS_FEED = "news_feed"
    COLLABORATION = "collaboration"
    LEARNING_PROGRESS = "learning_progress"
    PROJECT_STATUS = "project_status"
    SYSTEM_STATUS = "system_status"
    CUSTOM_WIDGET = "custom_widget"

class WidgetSize(Enum):
    """Widget size options"""
    SMALL = "small"         # 1x1 grid
    MEDIUM = "medium"       # 2x1 or 1x2 grid
    LARGE = "large"         # 2x2 grid
    XLARGE = "xlarge"       # 3x2 or 2x3 grid
    FULL_WIDTH = "full_width"  # Full row width

@dataclass
class WidgetConfig:
    """Configuration for a dashboard widget"""
    widget_id: str
    widget_type: WidgetType
    title: str
    size: WidgetSize
    position: Tuple[int, int]  # (row, column)
    settings: Dict[str, Any]
    is_visible: bool = True
    is_moveable: bool = True
    is_resizable: bool = True
    refresh_interval: int = 300  # seconds
    permissions: List[str] = None
    
    def __post_init__(self):
        if self.permissions is None:
            self.permissions = ["read"]

@dataclass
class DashboardLayout:
    """Dashboard layout configuration"""
    layout_id: str
    name: str
    layout_type: LayoutType
    columns: int
    rows: int
    widgets: List[WidgetConfig]
    theme: str = "default"
    is_responsive: bool = True
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow().isoformat()

@dataclass
class UserDashboard:
    """User-specific dashboard configuration"""
    user_id: str
    dashboard_id: str
    role: DashboardRole
    active_layout: str
    layouts: List[DashboardLayout]
    preferences: Dict[str, Any]
    usage_stats: Dict[str, Any]
    personalization_level: float  # 0.0 to 1.0
    created_at: str = None
    last_accessed: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.last_accessed is None:
            self.last_accessed = datetime.utcnow().isoformat()

class DashboardPersonalizer:
    """Personalizes dashboards based on user behavior and preferences"""
    
    def __init__(self):
        self.role_templates = {
            DashboardRole.DEVELOPER: self._create_developer_template,
            DashboardRole.BUSINESS_USER: self._create_business_template,
            DashboardRole.ANALYST: self._create_analyst_template,
            DashboardRole.MANAGER: self._create_manager_template,
            DashboardRole.ADMIN: self._create_admin_template,
            DashboardRole.CONTENT_CREATOR: self._create_content_creator_template,
            DashboardRole.STUDENT: self._create_student_template,
            DashboardRole.RESEARCHER: self._create_researcher_template,
        }
        
        self.usage_patterns = defaultdict(dict)
        self.personalization_rules = []
    
    async def create_personalized_dashboard(self, user_profile: Dict[str, Any], 
                                          usage_history: List[Dict[str, Any]]) -> UserDashboard:
        """Create a personalized dashboard for a user"""
        try:
            # Determine user role
            role = await self._determine_user_role(user_profile, usage_history)
            
            # Create base layout from template
            base_layout = await self._create_base_layout(role, user_profile)
            
            # Personalize based on usage patterns
            personalized_layout = await self._personalize_layout(
                base_layout, user_profile, usage_history
            )
            
            # Calculate personalization level
            personalization_level = await self._calculate_personalization_level(
                user_profile, usage_history
            )
            
            # Create dashboard
            dashboard = UserDashboard(
                user_id=user_profile.get('user_id', str(uuid.uuid4())),
                dashboard_id=str(uuid.uuid4()),
                role=role,
                active_layout=personalized_layout.layout_id,
                layouts=[personalized_layout],
                preferences=await self._extract_user_preferences(user_profile),
                usage_stats=await self._calculate_usage_stats(usage_history),
                personalization_level=personalization_level
            )
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error creating personalized dashboard: {e}")
            # Return default dashboard
            return await self._create_default_dashboard(user_profile.get('user_id', 'default'))
    
    async def _determine_user_role(self, user_profile: Dict[str, Any], 
                                 usage_history: List[Dict[str, Any]]) -> DashboardRole:
        """Determine the most appropriate role for the user"""
        try:
            # Check explicit role in profile
            if 'role' in user_profile:
                try:
                    return DashboardRole(user_profile['role'])
                except ValueError:
                    pass
            
            # Analyze interests and expertise
            interests = user_profile.get('interests', [])
            expertise = user_profile.get('expertise_level', 'intermediate')
            
            # Role detection based on interests
            if any(keyword in ' '.join(interests).lower() for keyword in ['programming', 'coding', 'development', 'api']):
                return DashboardRole.DEVELOPER
            elif any(keyword in ' '.join(interests).lower() for keyword in ['business', 'marketing', 'sales', 'strategy']):
                return DashboardRole.BUSINESS_USER
            elif any(keyword in ' '.join(interests).lower() for keyword in ['data', 'analytics', 'statistics', 'analysis']):
                return DashboardRole.ANALYST
            elif any(keyword in ' '.join(interests).lower() for keyword in ['content', 'writing', 'creative', 'design']):
                return DashboardRole.CONTENT_CREATOR
            elif any(keyword in ' '.join(interests).lower() for keyword in ['learning', 'education', 'student', 'study']):
                return DashboardRole.STUDENT
            elif any(keyword in ' '.join(interests).lower() for keyword in ['research', 'academic', 'science']):
                return DashboardRole.RESEARCHER
            elif expertise == 'expert' or 'management' in ' '.join(interests).lower():
                return DashboardRole.MANAGER
            
            # Analyze usage patterns
            if usage_history:
                usage_keywords = []
                for usage in usage_history:
                    if 'activity_type' in usage:
                        usage_keywords.append(usage['activity_type'].lower())
                
                usage_text = ' '.join(usage_keywords)
                
                if 'code' in usage_text or 'api' in usage_text:
                    return DashboardRole.DEVELOPER
                elif 'analytics' in usage_text or 'chart' in usage_text:
                    return DashboardRole.ANALYST
                elif 'admin' in usage_text or 'manage' in usage_text:
                    return DashboardRole.ADMIN
            
            # Default role
            return DashboardRole.BUSINESS_USER
            
        except Exception:
            return DashboardRole.BUSINESS_USER
    
    async def _create_base_layout(self, role: DashboardRole, 
                                user_profile: Dict[str, Any]) -> DashboardLayout:
        """Create base layout for user role"""
        try:
            template_creator = self.role_templates.get(role, self._create_business_template)
            return await template_creator(user_profile)
        except Exception as e:
            logger.error(f"Error creating base layout: {e}")
            return await self._create_default_layout()
    
    async def _create_developer_template(self, user_profile: Dict[str, Any]) -> DashboardLayout:
        """Create developer-focused dashboard template"""
        widgets = [
            WidgetConfig(
                widget_id="dev_ai_chat",
                widget_type=WidgetType.AI_CHAT,
                title="AI Assistant",
                size=WidgetSize.LARGE,
                position=(0, 0),
                settings={
                    "mode": "code_assistant",
                    "languages": ["python", "javascript", "typescript"],
                    "show_syntax_highlighting": True
                }
            ),
            WidgetConfig(
                widget_id="dev_quick_actions",
                widget_type=WidgetType.QUICK_ACTIONS,
                title="Quick Actions",
                size=WidgetSize.MEDIUM,
                position=(0, 2),
                settings={
                    "actions": [
                        {"name": "New Code Review", "icon": "code", "action": "create_review"},
                        {"name": "Run Tests", "icon": "play", "action": "run_tests"},
                        {"name": "Deploy", "icon": "upload", "action": "deploy"},
                        {"name": "Debug", "icon": "bug", "action": "debug"}
                    ]
                }
            ),
            WidgetConfig(
                widget_id="dev_project_status",
                widget_type=WidgetType.PROJECT_STATUS,
                title="Project Status",
                size=WidgetSize.MEDIUM,
                position=(1, 0),
                settings={
                    "show_build_status": True,
                    "show_test_results": True,
                    "show_coverage": True
                }
            ),
            WidgetConfig(
                widget_id="dev_recent_activity",
                widget_type=WidgetType.RECENT_ACTIVITY,
                title="Recent Activity",
                size=WidgetSize.MEDIUM,
                position=(1, 1),
                settings={
                    "activity_types": ["commits", "pull_requests", "issues", "deployments"],
                    "limit": 10
                }
            ),
            WidgetConfig(
                widget_id="dev_system_status",
                widget_type=WidgetType.SYSTEM_STATUS,
                title="System Health",
                size=WidgetSize.MEDIUM,
                position=(1, 2),
                settings={
                    "show_uptime": True,
                    "show_performance": True,
                    "show_errors": True
                }
            ),
            WidgetConfig(
                widget_id="dev_notes",
                widget_type=WidgetType.NOTES,
                title="Code Snippets",
                size=WidgetSize.MEDIUM,
                position=(2, 0),
                settings={
                    "syntax_highlighting": True,
                    "auto_save": True,
                    "categories": ["snippets", "todos", "ideas"]
                }
            )
        ]
        
        return DashboardLayout(
            layout_id=str(uuid.uuid4()),
            name="Developer Dashboard",
            layout_type=LayoutType.GRID,
            columns=3,
            rows=3,
            widgets=widgets,
            theme="dark"
        )
    
    async def _create_business_template(self, user_profile: Dict[str, Any]) -> DashboardLayout:
        """Create business user dashboard template"""
        widgets = [
            WidgetConfig(
                widget_id="biz_ai_chat",
                widget_type=WidgetType.AI_CHAT,
                title="Business Assistant",
                size=WidgetSize.LARGE,
                position=(0, 0),
                settings={
                    "mode": "business_advisor",
                    "focus_areas": ["strategy", "marketing", "sales", "operations"],
                    "show_suggestions": True
                }
            ),
            WidgetConfig(
                widget_id="biz_analytics",
                widget_type=WidgetType.ANALYTICS_CHART,
                title="Performance Analytics",
                size=WidgetSize.LARGE,
                position=(0, 2),
                settings={
                    "chart_types": ["line", "bar", "pie"],
                    "metrics": ["revenue", "users", "engagement", "conversion"],
                    "time_range": "30d"
                }
            ),
            WidgetConfig(
                widget_id="biz_quick_actions",
                widget_type=WidgetType.QUICK_ACTIONS,
                title="Quick Actions",
                size=WidgetSize.MEDIUM,
                position=(1, 0),
                settings={
                    "actions": [
                        {"name": "Create Report", "icon": "file-text", "action": "create_report"},
                        {"name": "Schedule Meeting", "icon": "calendar", "action": "schedule_meeting"},
                        {"name": "Send Email", "icon": "mail", "action": "compose_email"},
                        {"name": "View KPIs", "icon": "trending-up", "action": "view_kpis"}
                    ]
                }
            ),
            WidgetConfig(
                widget_id="biz_tasks",
                widget_type=WidgetType.TASKS,
                title="Tasks & Goals",
                size=WidgetSize.MEDIUM,
                position=(1, 1),
                settings={
                    "show_priority": True,
                    "show_due_dates": True,
                    "categories": ["urgent", "important", "planned"]
                }
            ),
            WidgetConfig(
                widget_id="biz_calendar",
                widget_type=WidgetType.CALENDAR,
                title="Schedule",
                size=WidgetSize.MEDIUM,
                position=(1, 2),
                settings={
                    "view": "week",
                    "show_conflicts": True,
                    "integration": "google_calendar"
                }
            ),
            WidgetConfig(
                widget_id="biz_notifications",
                widget_type=WidgetType.NOTIFICATIONS,
                title="Updates",
                size=WidgetSize.MEDIUM,
                position=(2, 0),
                settings={
                    "categories": ["alerts", "updates", "reminders"],
                    "show_unread_count": True
                }
            )
        ]
        
        return DashboardLayout(
            layout_id=str(uuid.uuid4()),
            name="Business Dashboard",
            layout_type=LayoutType.GRID,
            columns=3,
            rows=3,
            widgets=widgets,
            theme="light"
        )
    
    async def _create_analyst_template(self, user_profile: Dict[str, Any]) -> DashboardLayout:
        """Create analyst-focused dashboard template"""
        widgets = [
            WidgetConfig(
                widget_id="analyst_charts",
                widget_type=WidgetType.ANALYTICS_CHART,
                title="Data Visualization",
                size=WidgetSize.XLARGE,
                position=(0, 0),
                settings={
                    "chart_types": ["line", "scatter", "heatmap", "histogram"],
                    "data_sources": ["database", "api", "csv"],
                    "real_time": True
                }
            ),
            WidgetConfig(
                widget_id="analyst_ai_chat",
                widget_type=WidgetType.AI_CHAT,
                title="Data Assistant",
                size=WidgetSize.MEDIUM,
                position=(0, 2),
                settings={
                    "mode": "data_analyst",
                    "capabilities": ["sql_queries", "data_interpretation", "statistical_analysis"],
                    "show_code_examples": True
                }
            ),
            WidgetConfig(
                widget_id="analyst_metrics",
                widget_type=WidgetType.PERFORMANCE_METRICS,
                title="Key Metrics",
                size=WidgetSize.LARGE,
                position=(1, 0),
                settings={
                    "metrics": ["accuracy", "precision", "recall", "f1_score"],
                    "comparison_periods": ["1d", "7d", "30d"],
                    "alerts": True
                }
            ),
            WidgetConfig(
                widget_id="analyst_recent",
                widget_type=WidgetType.RECENT_ACTIVITY,
                title="Recent Analysis",
                size=WidgetSize.MEDIUM,
                position=(1, 2),
                settings={
                    "activity_types": ["queries", "reports", "models", "experiments"],
                    "show_results": True
                }
            )
        ]
        
        return DashboardLayout(
            layout_id=str(uuid.uuid4()),
            name="Analyst Dashboard",
            layout_type=LayoutType.VISUAL,
            columns=3,
            rows=2,
            widgets=widgets,
            theme="data"
        )
    
    async def _create_manager_template(self, user_profile: Dict[str, Any]) -> DashboardLayout:
        """Create manager dashboard template"""
        widgets = [
            WidgetConfig(
                widget_id="mgr_overview",
                widget_type=WidgetType.ANALYTICS_CHART,
                title="Team Overview",
                size=WidgetSize.XLARGE,
                position=(0, 0),
                settings={
                    "chart_types": ["dashboard", "kpi"],
                    "metrics": ["team_performance", "project_progress", "resource_utilization"],
                    "drill_down": True
                }
            ),
            WidgetConfig(
                widget_id="mgr_tasks",
                widget_type=WidgetType.PROJECT_STATUS,
                title="Project Status",
                size=WidgetSize.MEDIUM,
                position=(1, 0),
                settings={
                    "view": "timeline",
                    "show_dependencies": True,
                    "risk_indicators": True
                }
            ),
            WidgetConfig(
                widget_id="mgr_team",
                widget_type=WidgetType.COLLABORATION,
                title="Team Activity",
                size=WidgetSize.MEDIUM,
                position=(1, 1),
                settings={
                    "show_workload": True,
                    "show_availability": True,
                    "performance_indicators": True
                }
            ),
            WidgetConfig(
                widget_id="mgr_ai_chat",
                widget_type=WidgetType.AI_CHAT,
                title="Management Assistant",
                size=WidgetSize.MEDIUM,
                position=(1, 2),
                settings={
                    "mode": "management_advisor",
                    "focus_areas": ["team_management", "project_planning", "decision_support"],
                    "insights": True
                }
            )
        ]
        
        return DashboardLayout(
            layout_id=str(uuid.uuid4()),
            name="Manager Dashboard",
            layout_type=LayoutType.GRID,
            columns=3,
            rows=2,
            widgets=widgets,
            theme="executive"
        )
    
    async def _create_admin_template(self, user_profile: Dict[str, Any]) -> DashboardLayout:
        """Create admin dashboard template"""
        widgets = [
            WidgetConfig(
                widget_id="admin_system",
                widget_type=WidgetType.SYSTEM_STATUS,
                title="System Health",
                size=WidgetSize.LARGE,
                position=(0, 0),
                settings={
                    "show_all_services": True,
                    "real_time_monitoring": True,
                    "alert_integration": True
                }
            ),
            WidgetConfig(
                widget_id="admin_metrics",
                widget_type=WidgetType.PERFORMANCE_METRICS,
                title="Performance Metrics",
                size=WidgetSize.LARGE,
                position=(0, 2),
                settings={
                    "metrics": ["cpu", "memory", "disk", "network"],
                    "historical_data": True,
                    "predictive_alerts": True
                }
            ),
            WidgetConfig(
                widget_id="admin_users",
                widget_type=WidgetType.USER_PROFILE,
                title="User Management",
                size=WidgetSize.MEDIUM,
                position=(1, 0),
                settings={
                    "show_active_users": True,
                    "user_analytics": True,
                    "permission_management": True
                }
            ),
            WidgetConfig(
                widget_id="admin_logs",
                widget_type=WidgetType.RECENT_ACTIVITY,
                title="System Logs",
                size=WidgetSize.MEDIUM,
                position=(1, 1),
                settings={
                    "log_levels": ["error", "warning", "info"],
                    "real_time": True,
                    "filtering": True
                }
            ),
            WidgetConfig(
                widget_id="admin_quick_actions",
                widget_type=WidgetType.QUICK_ACTIONS,
                title="Admin Actions",
                size=WidgetSize.MEDIUM,
                position=(1, 2),
                settings={
                    "actions": [
                        {"name": "Restart Service", "icon": "refresh-cw", "action": "restart_service"},
                        {"name": "Backup Data", "icon": "download", "action": "backup"},
                        {"name": "Update System", "icon": "upload", "action": "update"},
                        {"name": "View Reports", "icon": "file-text", "action": "reports"}
                    ]
                }
            )
        ]
        
        return DashboardLayout(
            layout_id=str(uuid.uuid4()),
            name="Admin Dashboard",
            layout_type=LayoutType.GRID,
            columns=3,
            rows=2,
            widgets=widgets,
            theme="admin"
        )
    
    async def _create_content_creator_template(self, user_profile: Dict[str, Any]) -> DashboardLayout:
        """Create content creator dashboard template"""
        widgets = [
            WidgetConfig(
                widget_id="content_ai_chat",
                widget_type=WidgetType.AI_CHAT,
                title="Creative Assistant",
                size=WidgetSize.LARGE,
                position=(0, 0),
                settings={
                    "mode": "content_creator",
                    "capabilities": ["writing_assistant", "idea_generation", "editing_help"],
                    "creative_tools": True
                }
            ),
            WidgetConfig(
                widget_id="content_analytics",
                widget_type=WidgetType.ANALYTICS_CHART,
                title="Content Performance",
                size=WidgetSize.LARGE,
                position=(0, 2),
                settings={
                    "metrics": ["views", "engagement", "shares", "comments"],
                    "content_types": ["blog", "video", "social", "email"],
                    "trend_analysis": True
                }
            ),
            WidgetConfig(
                widget_id="content_calendar",
                widget_type=WidgetType.CALENDAR,
                title="Content Calendar",
                size=WidgetSize.MEDIUM,
                position=(1, 0),
                settings={
                    "view": "month",
                    "content_scheduling": True,
                    "deadline_tracking": True
                }
            ),
            WidgetConfig(
                widget_id="content_ideas",
                widget_type=WidgetType.NOTES,
                title="Ideas & Drafts",
                size=WidgetSize.MEDIUM,
                position=(1, 1),
                settings={
                    "categories": ["ideas", "drafts", "published"],
                    "rich_text": True,
                    "collaboration": True
                }
            ),
            WidgetConfig(
                widget_id="content_trends",
                widget_type=WidgetType.NEWS_FEED,
                title="Trending Topics",
                size=WidgetSize.MEDIUM,
                position=(1, 2),
                settings={
                    "sources": ["industry_news", "social_trends", "competitor_analysis"],
                    "keyword_tracking": True
                }
            )
        ]
        
        return DashboardLayout(
            layout_id=str(uuid.uuid4()),
            name="Content Creator Dashboard",
            layout_type=LayoutType.GRID,
            columns=3,
            rows=2,
            widgets=widgets,
            theme="creative"
        )
    
    async def _create_student_template(self, user_profile: Dict[str, Any]) -> DashboardLayout:
        """Create student dashboard template"""
        widgets = [
            WidgetConfig(
                widget_id="student_ai_chat",
                widget_type=WidgetType.AI_CHAT,
                title="Study Assistant",
                size=WidgetSize.LARGE,
                position=(0, 0),
                settings={
                    "mode": "tutor",
                    "subjects": ["math", "science", "programming", "writing"],
                    "adaptive_learning": True
                }
            ),
            WidgetConfig(
                widget_id="student_progress",
                widget_type=WidgetType.LEARNING_PROGRESS,
                title="Learning Progress",
                size=WidgetSize.LARGE,
                position=(0, 2),
                settings={
                    "show_achievements": True,
                    "progress_tracking": True,
                    "goal_setting": True
                }
            ),
            WidgetConfig(
                widget_id="student_calendar",
                widget_type=WidgetType.CALENDAR,
                title="Study Schedule",
                size=WidgetSize.MEDIUM,
                position=(1, 0),
                settings={
                    "view": "week",
                    "assignment_tracking": True,
                    "exam_reminders": True
                }
            ),
            WidgetConfig(
                widget_id="student_tasks",
                widget_type=WidgetType.TASKS,
                title="Assignments",
                size=WidgetSize.MEDIUM,
                position=(1, 1),
                settings={
                    "priority_sorting": True,
                    "due_date_alerts": True,
                    "completion_tracking": True
                }
            ),
            WidgetConfig(
                widget_id="student_notes",
                widget_type=WidgetType.NOTES,
                title="Study Notes",
                size=WidgetSize.MEDIUM,
                position=(1, 2),
                settings={
                    "organization": "subjects",
                    "search_functionality": True,
                    "study_guides": True
                }
            )
        ]
        
        return DashboardLayout(
            layout_id=str(uuid.uuid4()),
            name="Student Dashboard",
            layout_type=LayoutType.GRID,
            columns=3,
            rows=2,
            widgets=widgets,
            theme="education"
        )
    
    async def _create_researcher_template(self, user_profile: Dict[str, Any]) -> DashboardLayout:
        """Create researcher dashboard template"""
        widgets = [
            WidgetConfig(
                widget_id="research_ai_chat",
                widget_type=WidgetType.AI_CHAT,
                title="Research Assistant",
                size=WidgetSize.LARGE,
                position=(0, 0),
                settings={
                    "mode": "research_assistant",
                    "capabilities": ["literature_review", "data_analysis", "hypothesis_testing"],
                    "citation_support": True
                }
            ),
            WidgetConfig(
                widget_id="research_data",
                widget_type=WidgetType.ANALYTICS_CHART,
                title="Research Data",
                size=WidgetSize.LARGE,
                position=(0, 2),
                settings={
                    "chart_types": ["scatter", "correlation", "regression"],
                    "statistical_tools": True,
                    "export_options": ["csv", "pdf", "latex"]
                }
            ),
            WidgetConfig(
                widget_id="research_papers",
                widget_type=WidgetType.NOTES,
                title="Research Papers",
                size=WidgetSize.MEDIUM,
                position=(1, 0),
                settings={
                    "citation_manager": True,
                    "pdf_annotation": True,
                    "reference_linking": True
                }
            ),
            WidgetConfig(
                widget_id="research_progress",
                widget_type=WidgetType.PROJECT_STATUS,
                title="Research Progress",
                size=WidgetSize.MEDIUM,
                position=(1, 1),
                settings={
                    "milestone_tracking": True,
                    "publication_timeline": True,
                    "collaboration_tools": True
                }
            ),
            WidgetConfig(
                widget_id="research_news",
                widget_type=WidgetType.NEWS_FEED,
                title="Academic News",
                size=WidgetSize.MEDIUM,
                position=(1, 2),
                settings={
                    "sources": ["arxiv", "pubmed", "google_scholar"],
                    "keyword_alerts": True,
                    "peer_recommendations": True
                }
            )
        ]
        
        return DashboardLayout(
            layout_id=str(uuid.uuid4()),
            name="Researcher Dashboard",
            layout_type=LayoutType.GRID,
            columns=3,
            rows=2,
            widgets=widgets,
            theme="academic"
        )
    
    async def _personalize_layout(self, base_layout: DashboardLayout,
                                user_profile: Dict[str, Any],
                                usage_history: List[Dict[str, Any]]) -> DashboardLayout:
        """Personalize layout based on user behavior"""
        try:
            # Analyze usage patterns
            widget_usage = await self._analyze_widget_usage(usage_history)
            
            # Adjust widget sizes based on usage
            for widget in base_layout.widgets:
                usage_score = widget_usage.get(widget.widget_type.value, 0)
                if usage_score > 0.8:  # High usage
                    if widget.size in [WidgetSize.SMALL, WidgetSize.MEDIUM]:
                        widget.size = WidgetSize.LARGE
                elif usage_score < 0.2:  # Low usage
                    if widget.size in [WidgetSize.LARGE, WidgetSize.XLARGE]:
                        widget.size = WidgetSize.MEDIUM
            
            # Remove rarely used widgets
            base_layout.widgets = [
                widget for widget in base_layout.widgets
                if widget_usage.get(widget.widget_type.value, 0.5) > 0.1
            ]
            
            # Add frequently requested widgets
            missing_widgets = await self._identify_missing_widgets(
                base_layout, user_profile, usage_history
            )
            base_layout.widgets.extend(missing_widgets)
            
            # Optimize layout
            base_layout = await self._optimize_widget_positions(base_layout, widget_usage)
            
            # Update timestamp
            base_layout.updated_at = datetime.utcnow().isoformat()
            
            return base_layout
            
        except Exception as e:
            logger.error(f"Error personalizing layout: {e}")
            return base_layout
    
    async def _analyze_widget_usage(self, usage_history: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze widget usage patterns"""
        try:
            widget_interactions = defaultdict(int)
            total_interactions = 0
            
            for usage in usage_history:
                if 'widget_type' in usage:
                    widget_interactions[usage['widget_type']] += 1
                    total_interactions += 1
            
            # Calculate usage scores (0.0 to 1.0)
            usage_scores = {}
            for widget_type, count in widget_interactions.items():
                usage_scores[widget_type] = count / max(total_interactions, 1)
            
            return usage_scores
            
        except Exception:
            return {}
    
    async def _identify_missing_widgets(self, layout: DashboardLayout,
                                       user_profile: Dict[str, Any],
                                       usage_history: List[Dict[str, Any]]) -> List[WidgetConfig]:
        """Identify widgets that should be added based on user behavior"""
        try:
            missing_widgets = []
            current_widget_types = {widget.widget_type for widget in layout.widgets}
            
            # Check for commonly requested widget types
            requested_types = []
            for usage in usage_history:
                if 'requested_widget' in usage:
                    requested_types.append(usage['requested_widget'])
            
            # Add weather widget for users who check it frequently
            if ('weather' in requested_types or 
                any('weather' in interest.lower() for interest in user_profile.get('interests', []))):
                if WidgetType.WEATHER not in current_widget_types:
                    missing_widgets.append(
                        WidgetConfig(
                            widget_id="weather_widget",
                            widget_type=WidgetType.WEATHER,
                            title="Weather",
                            size=WidgetSize.SMALL,
                            position=(0, 0),  # Will be repositioned
                            settings={"location": "auto", "units": "metric"}
                        )
                    )
            
            return missing_widgets
            
        except Exception:
            return []
    
    async def _optimize_widget_positions(self, layout: DashboardLayout,
                                        usage_scores: Dict[str, float]) -> DashboardLayout:
        """Optimize widget positions based on usage patterns"""
        try:
            # Sort widgets by usage score (most used first)
            layout.widgets.sort(
                key=lambda w: usage_scores.get(w.widget_type.value, 0.5),
                reverse=True
            )
            
            # Reassign positions in a grid
            col = 0
            row = 0
            
            for widget in layout.widgets:
                widget.position = (row, col)
                
                # Move to next position based on widget size
                if widget.size in [WidgetSize.LARGE, WidgetSize.XLARGE, WidgetSize.FULL_WIDTH]:
                    col += 2
                else:
                    col += 1
                
                if col >= layout.columns:
                    col = 0
                    row += 1
            
            # Update layout dimensions if needed
            layout.rows = max(row + 1, layout.rows)
            
            return layout
            
        except Exception as e:
            logger.error(f"Error optimizing positions: {e}")
            return layout
    
    async def _calculate_personalization_level(self, user_profile: Dict[str, Any],
                                              usage_history: List[Dict[str, Any]]) -> float:
        """Calculate how personalized the dashboard is"""
        try:
            factors = []
            
            # Profile completeness
            profile_fields = ['interests', 'expertise_level', 'communication_style', 'preferences']
            completed_fields = sum(1 for field in profile_fields if user_profile.get(field))
            factors.append(completed_fields / len(profile_fields))
            
            # Usage history depth
            if usage_history:
                usage_depth = min(len(usage_history) / 50, 1.0)  # Normalize to 50 interactions
                factors.append(usage_depth)
            else:
                factors.append(0.0)
            
            # Customization level
            customizations = user_profile.get('customizations', 0)
            customization_score = min(customizations / 10, 1.0)  # Normalize to 10 customizations
            factors.append(customization_score)
            
            return sum(factors) / len(factors) if factors else 0.0
            
        except Exception:
            return 0.5
    
    async def _extract_user_preferences(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Extract user preferences for dashboard"""
        try:
            return {
                'theme': user_profile.get('preferred_theme', 'light'),
                'layout_density': user_profile.get('layout_density', 'normal'),
                'animation_enabled': user_profile.get('animations', True),
                'notifications_enabled': user_profile.get('notifications', True),
                'auto_refresh': user_profile.get('auto_refresh', True),
                'compact_mode': user_profile.get('compact_mode', False),
                'accessibility': user_profile.get('accessibility_options', {}),
                'language': user_profile.get('language', 'en'),
                'timezone': user_profile.get('timezone', 'UTC')
            }
        except Exception:
            return {}
    
    async def _calculate_usage_stats(self, usage_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate usage statistics"""
        try:
            if not usage_history:
                return {}
            
            # Time-based stats
            daily_usage = defaultdict(int)
            hourly_usage = defaultdict(int)
            
            for usage in usage_history:
                if 'timestamp' in usage:
                    try:
                        dt = datetime.fromisoformat(usage['timestamp'])
                        daily_usage[dt.date().isoformat()] += 1
                        hourly_usage[dt.hour] += 1
                    except:
                        continue
            
            # Most active day and hour
            most_active_day = max(daily_usage, key=daily_usage.get) if daily_usage else None
            most_active_hour = max(hourly_usage, key=hourly_usage.get) if hourly_usage else None
            
            return {
                'total_interactions': len(usage_history),
                'daily_average': len(usage_history) / max(len(daily_usage), 1),
                'most_active_day': most_active_day,
                'most_active_hour': most_active_hour,
                'usage_pattern': 'regular' if len(daily_usage) > 7 else 'sporadic'
            }
            
        except Exception:
            return {}
    
    async def _create_default_layout(self) -> DashboardLayout:
        """Create a default layout as fallback"""
        widgets = [
            WidgetConfig(
                widget_id="default_ai_chat",
                widget_type=WidgetType.AI_CHAT,
                title="AI Assistant",
                size=WidgetSize.LARGE,
                position=(0, 0),
                settings={"mode": "general_assistant"}
            ),
            WidgetConfig(
                widget_id="default_quick_actions",
                widget_type=WidgetType.QUICK_ACTIONS,
                title="Quick Actions",
                size=WidgetSize.MEDIUM,
                position=(0, 2),
                settings={
                    "actions": [
                        {"name": "New Chat", "icon": "message-square", "action": "new_chat"},
                        {"name": "Settings", "icon": "settings", "action": "open_settings"}
                    ]
                }
            ),
            WidgetConfig(
                widget_id="default_recent",
                widget_type=WidgetType.RECENT_ACTIVITY,
                title="Recent Activity",
                size=WidgetSize.MEDIUM,
                position=(1, 0),
                settings={"limit": 5}
            )
        ]
        
        return DashboardLayout(
            layout_id=str(uuid.uuid4()),
            name="Default Dashboard",
            layout_type=LayoutType.GRID,
            columns=3,
            rows=2,
            widgets=widgets
        )
    
    async def _create_default_dashboard(self, user_id: str) -> UserDashboard:
        """Create a default dashboard"""
        default_layout = await self._create_default_layout()
        
        return UserDashboard(
            user_id=user_id,
            dashboard_id=str(uuid.uuid4()),
            role=DashboardRole.BUSINESS_USER,
            active_layout=default_layout.layout_id,
            layouts=[default_layout],
            preferences={},
            usage_stats={},
            personalization_level=0.0
        )

class DashboardManager:
    """Manages dashboard operations and adaptations"""
    
    def __init__(self):
        self.personalizer = DashboardPersonalizer()
        self.dashboards = {}  # In-memory storage (would be database in production)
        self.usage_tracker = defaultdict(list)
        self.adaptation_rules = []
    
    async def create_dashboard(self, user_profile: Dict[str, Any],
                              usage_history: Optional[List[Dict[str, Any]]] = None) -> UserDashboard:
        """Create a new personalized dashboard"""
        try:
            if usage_history is None:
                usage_history = []
            
            dashboard = await self.personalizer.create_personalized_dashboard(
                user_profile, usage_history
            )
            
            # Store dashboard
            self.dashboards[dashboard.dashboard_id] = dashboard
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            return await self.personalizer._create_default_dashboard(
                user_profile.get('user_id', 'error_user')
            )
    
    async def get_dashboard(self, dashboard_id: str) -> Optional[UserDashboard]:
        """Get dashboard by ID"""
        return self.dashboards.get(dashboard_id)
    
    async def update_dashboard(self, dashboard_id: str, 
                              updates: Dict[str, Any]) -> Optional[UserDashboard]:
        """Update dashboard configuration"""
        try:
            dashboard = self.dashboards.get(dashboard_id)
            if not dashboard:
                return None
            
            # Update dashboard properties
            for key, value in updates.items():
                if hasattr(dashboard, key):
                    setattr(dashboard, key, value)
            
            # Update timestamp
            dashboard.last_accessed = datetime.utcnow().isoformat()
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")
            return None
    
    async def adapt_dashboard(self, dashboard_id: str,
                             interaction_data: Dict[str, Any]) -> Optional[UserDashboard]:
        """Adapt dashboard based on user interactions"""
        try:
            dashboard = self.dashboards.get(dashboard_id)
            if not dashboard:
                return None
            
            # Track usage
            self.usage_tracker[dashboard.user_id].append({
                **interaction_data,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Check if adaptation is needed
            should_adapt = await self._should_adapt_dashboard(dashboard, interaction_data)
            
            if should_adapt:
                # Re-personalize dashboard
                user_profile = {
                    'user_id': dashboard.user_id,
                    'role': dashboard.role.value,
                    'preferences': dashboard.preferences
                }
                
                updated_dashboard = await self.personalizer.create_personalized_dashboard(
                    user_profile, self.usage_tracker[dashboard.user_id]
                )
                
                # Preserve dashboard ID and metadata
                updated_dashboard.dashboard_id = dashboard_id
                updated_dashboard.created_at = dashboard.created_at
                
                # Update stored dashboard
                self.dashboards[dashboard_id] = updated_dashboard
                
                return updated_dashboard
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error adapting dashboard: {e}")
            return dashboard
    
    async def _should_adapt_dashboard(self, dashboard: UserDashboard,
                                     interaction_data: Dict[str, Any]) -> bool:
        """Determine if dashboard should be adapted"""
        try:
            # Adapt if significant usage pattern changes
            user_usage = self.usage_tracker[dashboard.user_id]
            
            # Check for pattern changes every 100 interactions
            if len(user_usage) % 100 == 0 and len(user_usage) > 0:
                return True
            
            # Check for specific triggers
            if interaction_data.get('widget_added') or interaction_data.get('layout_changed'):
                return True
            
            # Check for low usage of current widgets
            recent_usage = user_usage[-50:] if len(user_usage) > 50 else user_usage
            widget_usage = defaultdict(int)
            
            for usage in recent_usage:
                if 'widget_type' in usage:
                    widget_usage[usage['widget_type']] += 1
            
            # If any widget has very low usage, consider adaptation
            for widget in dashboard.layouts[0].widgets:  # Check active layout
                if widget_usage.get(widget.widget_type.value, 0) < 2:  # Less than 2 uses in 50 interactions
                    return True
            
            return False
            
        except Exception:
            return False
    
    async def get_dashboard_analytics(self, dashboard_id: str) -> Dict[str, Any]:
        """Get analytics for a dashboard"""
        try:
            dashboard = self.dashboards.get(dashboard_id)
            if not dashboard:
                return {}
            
            user_usage = self.usage_tracker[dashboard.user_id]
            
            # Widget usage analytics
            widget_usage = defaultdict(int)
            for usage in user_usage:
                if 'widget_type' in usage:
                    widget_usage[usage['widget_type']] += 1
            
            # Time-based analytics
            hourly_usage = defaultdict(int)
            daily_usage = defaultdict(int)
            
            for usage in user_usage:
                if 'timestamp' in usage:
                    try:
                        dt = datetime.fromisoformat(usage['timestamp'])
                        hourly_usage[dt.hour] += 1
                        daily_usage[dt.date().isoformat()] += 1
                    except:
                        continue
            
            return {
                'dashboard_info': {
                    'id': dashboard.dashboard_id,
                    'role': dashboard.role.value,
                    'personalization_level': dashboard.personalization_level,
                    'widget_count': len(dashboard.layouts[0].widgets),
                    'layout_type': dashboard.layouts[0].layout_type.value
                },
                'usage_analytics': {
                    'total_interactions': len(user_usage),
                    'widget_usage': dict(widget_usage),
                    'most_used_widget': max(widget_usage, key=widget_usage.get) if widget_usage else None,
                    'hourly_distribution': dict(hourly_usage),
                    'daily_usage': dict(daily_usage),
                    'peak_hour': max(hourly_usage, key=hourly_usage.get) if hourly_usage else None
                },
                'personalization_metrics': {
                    'adaptation_count': len([u for u in user_usage if u.get('dashboard_adapted')]),
                    'customization_count': len([u for u in user_usage if u.get('widget_customized')]),
                    'satisfaction_indicators': dashboard.usage_stats
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard analytics: {e}")
            return {}
    
    async def export_dashboard(self, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """Export dashboard configuration"""
        try:
            dashboard = self.dashboards.get(dashboard_id)
            if not dashboard:
                return None
            
            # Convert dashboard to serializable dict
            dashboard_dict = asdict(dashboard)
            
            # Convert enums to their values
            dashboard_dict['role'] = dashboard.role.value
            
            for layout in dashboard_dict['layouts']:
                layout['layout_type'] = layout['layout_type'].value if hasattr(layout['layout_type'], 'value') else layout['layout_type']
                
                for widget in layout['widgets']:
                    widget['widget_type'] = widget['widget_type'].value if hasattr(widget['widget_type'], 'value') else widget['widget_type']
                    widget['size'] = widget['size'].value if hasattr(widget['size'], 'value') else widget['size']
            
            return {
                'dashboard': dashboard_dict,
                'export_timestamp': datetime.utcnow().isoformat(),
                'version': '1.0'
            }
            
        except Exception as e:
            logger.error(f"Error exporting dashboard: {e}")
            return None
    
    async def import_dashboard(self, dashboard_data: Dict[str, Any]) -> Optional[str]:
        """Import dashboard configuration"""
        try:
            # Validate data structure
            if 'dashboard' not in dashboard_data:
                return None
            
            dashboard_dict = dashboard_data['dashboard']
            
            # Reconstruct dashboard object
            # Convert layouts
            layouts = []
            for layout_dict in dashboard_dict.get('layouts', []):
                widgets = []
                for widget_dict in layout_dict.get('widgets', []):
                    widget = WidgetConfig(
                        widget_id=widget_dict['widget_id'],
                        widget_type=WidgetType(widget_dict['widget_type']),
                        title=widget_dict['title'],
                        size=WidgetSize(widget_dict['size']),
                        position=tuple(widget_dict['position']),
                        settings=widget_dict['settings'],
                        is_visible=widget_dict.get('is_visible', True),
                        is_moveable=widget_dict.get('is_moveable', True),
                        is_resizable=widget_dict.get('is_resizable', True),
                        refresh_interval=widget_dict.get('refresh_interval', 300),
                        permissions=widget_dict.get('permissions', ['read'])
                    )
                    widgets.append(widget)
                
                layout = DashboardLayout(
                    layout_id=layout_dict['layout_id'],
                    name=layout_dict['name'],
                    layout_type=LayoutType(layout_dict['layout_type']),
                    columns=layout_dict['columns'],
                    rows=layout_dict['rows'],
                    widgets=widgets,
                    theme=layout_dict.get('theme', 'default'),
                    is_responsive=layout_dict.get('is_responsive', True),
                    created_at=layout_dict.get('created_at'),
                    updated_at=layout_dict.get('updated_at')
                )
                layouts.append(layout)
            
            # Create dashboard
            dashboard = UserDashboard(
                user_id=dashboard_dict['user_id'],
                dashboard_id=str(uuid.uuid4()),  # Generate new ID
                role=DashboardRole(dashboard_dict['role']),
                active_layout=dashboard_dict['active_layout'],
                layouts=layouts,
                preferences=dashboard_dict.get('preferences', {}),
                usage_stats=dashboard_dict.get('usage_stats', {}),
                personalization_level=dashboard_dict.get('personalization_level', 0.0),
                created_at=dashboard_dict.get('created_at'),
                last_accessed=datetime.utcnow().isoformat()
            )
            
            # Store dashboard
            self.dashboards[dashboard.dashboard_id] = dashboard
            
            return dashboard.dashboard_id
            
        except Exception as e:
            logger.error(f"Error importing dashboard: {e}")
            return None

# Global manager instance
dashboard_manager = DashboardManager()

# Export main classes and functions
__all__ = [
    'DashboardRole',
    'LayoutType', 
    'WidgetType',
    'WidgetSize',
    'WidgetConfig',
    'DashboardLayout',
    'UserDashboard',
    'DashboardPersonalizer',
    'DashboardManager',
    'dashboard_manager'
]
