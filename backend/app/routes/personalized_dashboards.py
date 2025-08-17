"""
Task 2.2.4: Personalized Dashboards - API Routes
REST API endpoints for personalized dashboard management and customization.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import logging

from ..services.personalized_dashboards import (
    dashboard_manager,
    DashboardRole,
    LayoutType,
    WidgetType,
    WidgetSize,
    WidgetConfig,
    DashboardLayout,
    UserDashboard
)

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v1/dashboards", tags=["Personalized Dashboards"])

# Request/Response Models
class WidgetConfigModel(BaseModel):
    """Widget configuration model"""
    widget_id: str = Field(..., description="Unique widget identifier")
    widget_type: str = Field(..., description="Widget type")
    title: str = Field(..., description="Widget title")
    size: str = Field(..., description="Widget size")
    position: Tuple[int, int] = Field(..., description="Widget position (row, column)")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Widget settings")
    is_visible: bool = Field(default=True, description="Widget visibility")
    is_moveable: bool = Field(default=True, description="Whether widget can be moved")
    is_resizable: bool = Field(default=True, description="Whether widget can be resized")
    refresh_interval: int = Field(default=300, description="Refresh interval in seconds")
    permissions: List[str] = Field(default=["read"], description="Widget permissions")

class DashboardLayoutModel(BaseModel):
    """Dashboard layout model"""
    layout_id: str = Field(..., description="Unique layout identifier")
    name: str = Field(..., description="Layout name")
    layout_type: str = Field(..., description="Layout type")
    columns: int = Field(..., description="Number of columns")
    rows: int = Field(..., description="Number of rows")
    widgets: List[WidgetConfigModel] = Field(..., description="Layout widgets")
    theme: str = Field(default="default", description="Layout theme")
    is_responsive: bool = Field(default=True, description="Responsive layout")
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Update timestamp")

class UserDashboardModel(BaseModel):
    """User dashboard model"""
    user_id: str = Field(..., description="User identifier")
    dashboard_id: str = Field(..., description="Dashboard identifier")
    role: str = Field(..., description="User role")
    active_layout: str = Field(..., description="Active layout ID")
    layouts: List[DashboardLayoutModel] = Field(..., description="Available layouts")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")
    usage_stats: Dict[str, Any] = Field(default_factory=dict, description="Usage statistics")
    personalization_level: float = Field(..., description="Personalization level (0.0-1.0)")
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    last_accessed: Optional[str] = Field(default=None, description="Last access timestamp")

class CreateDashboardRequest(BaseModel):
    """Request to create a new dashboard"""
    user_profile: Dict[str, Any] = Field(..., description="User profile information")
    usage_history: List[Dict[str, Any]] = Field(default_factory=list, description="User usage history")
    role_override: Optional[str] = Field(default=None, description="Override automatic role detection")

class UpdateDashboardRequest(BaseModel):
    """Request to update dashboard"""
    updates: Dict[str, Any] = Field(..., description="Dashboard updates")

class AdaptDashboardRequest(BaseModel):
    """Request to adapt dashboard based on interaction"""
    interaction_data: Dict[str, Any] = Field(..., description="Interaction data")

class WidgetInteractionRequest(BaseModel):
    """Widget interaction tracking"""
    widget_id: str = Field(..., description="Widget ID")
    widget_type: str = Field(..., description="Widget type")
    interaction_type: str = Field(..., description="Interaction type (click, resize, move, etc.)")
    duration_seconds: Optional[float] = Field(default=None, description="Interaction duration")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class DashboardAnalyticsResponse(BaseModel):
    """Dashboard analytics response"""
    dashboard_info: Dict[str, Any] = Field(..., description="Dashboard information")
    usage_analytics: Dict[str, Any] = Field(..., description="Usage analytics")
    personalization_metrics: Dict[str, Any] = Field(..., description="Personalization metrics")

class ExportDashboardResponse(BaseModel):
    """Dashboard export response"""
    dashboard: Dict[str, Any] = Field(..., description="Dashboard data")
    export_timestamp: str = Field(..., description="Export timestamp")
    version: str = Field(..., description="Export version")

class ImportDashboardRequest(BaseModel):
    """Dashboard import request"""
    dashboard_data: Dict[str, Any] = Field(..., description="Dashboard data to import")

# API Endpoints

@router.post("/create", response_model=UserDashboardModel)
async def create_personalized_dashboard(request: CreateDashboardRequest) -> UserDashboardModel:
    """
    Create a personalized dashboard based on user profile and usage history.
    
    Analyzes user preferences, role, and behavior patterns to create an optimized
    dashboard layout with relevant widgets and intelligent positioning.
    """
    try:
        # Apply role override if specified
        if request.role_override:
            request.user_profile['role'] = request.role_override
        
        # Create dashboard
        dashboard = await dashboard_manager.create_dashboard(
            user_profile=request.user_profile,
            usage_history=request.usage_history
        )
        
        # Convert to response model
        return _convert_dashboard_to_model(dashboard)
        
    except Exception as e:
        logger.error(f"Error creating personalized dashboard: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create personalized dashboard: {str(e)}"
        )

@router.get("/{dashboard_id}", response_model=UserDashboardModel)
async def get_dashboard(dashboard_id: str) -> UserDashboardModel:
    """
    Retrieve a specific dashboard by ID.
    
    Returns complete dashboard configuration including layouts, widgets,
    and personalization settings.
    """
    try:
        dashboard = await dashboard_manager.get_dashboard(dashboard_id)
        
        if not dashboard:
            raise HTTPException(
                status_code=404,
                detail=f"Dashboard {dashboard_id} not found"
            )
        
        return _convert_dashboard_to_model(dashboard)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving dashboard: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve dashboard: {str(e)}"
        )

@router.put("/{dashboard_id}", response_model=UserDashboardModel)
async def update_dashboard(dashboard_id: str, request: UpdateDashboardRequest) -> UserDashboardModel:
    """
    Update dashboard configuration.
    
    Allows modification of dashboard settings, layout preferences,
    and widget configurations.
    """
    try:
        updated_dashboard = await dashboard_manager.update_dashboard(
            dashboard_id=dashboard_id,
            updates=request.updates
        )
        
        if not updated_dashboard:
            raise HTTPException(
                status_code=404,
                detail=f"Dashboard {dashboard_id} not found"
            )
        
        return _convert_dashboard_to_model(updated_dashboard)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating dashboard: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update dashboard: {str(e)}"
        )

@router.post("/{dashboard_id}/adapt", response_model=UserDashboardModel)
async def adapt_dashboard(dashboard_id: str, request: AdaptDashboardRequest) -> UserDashboardModel:
    """
    Adapt dashboard based on user interactions.
    
    Uses machine learning to optimize dashboard layout and widget selection
    based on user behavior patterns.
    """
    try:
        adapted_dashboard = await dashboard_manager.adapt_dashboard(
            dashboard_id=dashboard_id,
            interaction_data=request.interaction_data
        )
        
        if not adapted_dashboard:
            raise HTTPException(
                status_code=404,
                detail=f"Dashboard {dashboard_id} not found"
            )
        
        return _convert_dashboard_to_model(adapted_dashboard)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adapting dashboard: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to adapt dashboard: {str(e)}"
        )

@router.post("/{dashboard_id}/track-interaction")
async def track_widget_interaction(dashboard_id: str, interaction: WidgetInteractionRequest) -> Dict[str, Any]:
    """
    Track widget interaction for analytics and adaptation.
    
    Records user interactions with dashboard widgets to improve
    personalization and identify usage patterns.
    """
    try:
        # Build interaction data
        interaction_data = {
            'widget_id': interaction.widget_id,
            'widget_type': interaction.widget_type,
            'interaction_type': interaction.interaction_type,
            'duration_seconds': interaction.duration_seconds,
            'timestamp': datetime.utcnow().isoformat(),
            **interaction.metadata
        }
        
        # Track the interaction (this could trigger adaptation)
        adapted_dashboard = await dashboard_manager.adapt_dashboard(
            dashboard_id=dashboard_id,
            interaction_data=interaction_data
        )
        
        return {
            'status': 'success',
            'interaction_tracked': True,
            'dashboard_adapted': adapted_dashboard is not None,
            'timestamp': interaction_data['timestamp']
        }
        
    except Exception as e:
        logger.error(f"Error tracking widget interaction: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to track interaction: {str(e)}"
        )

@router.get("/{dashboard_id}/analytics", response_model=DashboardAnalyticsResponse)
async def get_dashboard_analytics(dashboard_id: str) -> DashboardAnalyticsResponse:
    """
    Get comprehensive analytics for a dashboard.
    
    Returns usage patterns, widget performance, personalization metrics,
    and optimization recommendations.
    """
    try:
        analytics = await dashboard_manager.get_dashboard_analytics(dashboard_id)
        
        if not analytics:
            raise HTTPException(
                status_code=404,
                detail=f"Dashboard {dashboard_id} not found or no analytics available"
            )
        
        return DashboardAnalyticsResponse(**analytics)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dashboard analytics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analytics: {str(e)}"
        )

@router.get("/{dashboard_id}/export", response_model=ExportDashboardResponse)
async def export_dashboard(dashboard_id: str) -> ExportDashboardResponse:
    """
    Export dashboard configuration for backup or sharing.
    
    Returns complete dashboard data in a portable format that can
    be imported into other systems or restored later.
    """
    try:
        export_data = await dashboard_manager.export_dashboard(dashboard_id)
        
        if not export_data:
            raise HTTPException(
                status_code=404,
                detail=f"Dashboard {dashboard_id} not found"
            )
        
        return ExportDashboardResponse(**export_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting dashboard: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export dashboard: {str(e)}"
        )

@router.post("/import", response_model=Dict[str, str])
async def import_dashboard(request: ImportDashboardRequest) -> Dict[str, str]:
    """
    Import dashboard configuration from exported data.
    
    Creates a new dashboard instance from previously exported data,
    allowing for dashboard backup/restore and sharing functionality.
    """
    try:
        dashboard_id = await dashboard_manager.import_dashboard(request.dashboard_data)
        
        if not dashboard_id:
            raise HTTPException(
                status_code=400,
                detail="Invalid dashboard data or import failed"
            )
        
        return {
            'status': 'success',
            'dashboard_id': dashboard_id,
            'message': 'Dashboard imported successfully'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing dashboard: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to import dashboard: {str(e)}"
        )

@router.get("/roles/available", response_model=List[Dict[str, str]])
async def get_available_roles() -> List[Dict[str, str]]:
    """
    Get list of available dashboard roles.
    
    Returns all supported user roles with descriptions for
    dashboard personalization and template selection.
    """
    try:
        roles = [
            {
                "role": DashboardRole.DEVELOPER.value,
                "name": "Developer",
                "description": "Code-focused dashboard with development tools and metrics"
            },
            {
                "role": DashboardRole.BUSINESS_USER.value,
                "name": "Business User",
                "description": "Business-oriented dashboard with analytics and management tools"
            },
            {
                "role": DashboardRole.ANALYST.value,
                "name": "Analyst",
                "description": "Data analysis dashboard with visualization and statistical tools"
            },
            {
                "role": DashboardRole.MANAGER.value,
                "name": "Manager",
                "description": "Management dashboard with team oversight and project tracking"
            },
            {
                "role": DashboardRole.ADMIN.value,
                "name": "Administrator",
                "description": "System administration dashboard with monitoring and control tools"
            },
            {
                "role": DashboardRole.CONTENT_CREATOR.value,
                "name": "Content Creator",
                "description": "Creative dashboard with content management and performance tools"
            },
            {
                "role": DashboardRole.STUDENT.value,
                "name": "Student",
                "description": "Learning-focused dashboard with study tools and progress tracking"
            },
            {
                "role": DashboardRole.RESEARCHER.value,
                "name": "Researcher",
                "description": "Research dashboard with academic tools and literature management"
            }
        ]
        
        return roles
        
    except Exception as e:
        logger.error(f"Error getting available roles: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get available roles: {str(e)}"
        )

@router.get("/widget-types/available", response_model=List[Dict[str, str]])
async def get_available_widget_types() -> List[Dict[str, str]]:
    """
    Get list of available widget types.
    
    Returns all supported widget types with descriptions for
    dashboard customization and widget selection.
    """
    try:
        widget_types = [
            {
                "type": WidgetType.AI_CHAT.value,
                "name": "AI Chat",
                "description": "Interactive AI assistant widget"
            },
            {
                "type": WidgetType.CONVERSATION_LIST.value,
                "name": "Conversation List",
                "description": "List of recent conversations"
            },
            {
                "type": WidgetType.ANALYTICS_CHART.value,
                "name": "Analytics Chart",
                "description": "Data visualization and charts"
            },
            {
                "type": WidgetType.QUICK_ACTIONS.value,
                "name": "Quick Actions",
                "description": "Frequently used action buttons"
            },
            {
                "type": WidgetType.RECENT_ACTIVITY.value,
                "name": "Recent Activity",
                "description": "Timeline of recent activities"
            },
            {
                "type": WidgetType.PERFORMANCE_METRICS.value,
                "name": "Performance Metrics",
                "description": "Key performance indicators and metrics"
            },
            {
                "type": WidgetType.USER_PROFILE.value,
                "name": "User Profile",
                "description": "User information and settings"
            },
            {
                "type": WidgetType.NOTIFICATIONS.value,
                "name": "Notifications",
                "description": "System and user notifications"
            },
            {
                "type": WidgetType.FAVORITES.value,
                "name": "Favorites",
                "description": "Bookmarked items and shortcuts"
            },
            {
                "type": WidgetType.SEARCH.value,
                "name": "Search",
                "description": "Search functionality widget"
            },
            {
                "type": WidgetType.CALENDAR.value,
                "name": "Calendar",
                "description": "Schedule and event management"
            },
            {
                "type": WidgetType.TASKS.value,
                "name": "Tasks",
                "description": "Task and todo management"
            },
            {
                "type": WidgetType.NOTES.value,
                "name": "Notes",
                "description": "Note-taking and documentation"
            },
            {
                "type": WidgetType.WEATHER.value,
                "name": "Weather",
                "description": "Weather information widget"
            },
            {
                "type": WidgetType.NEWS_FEED.value,
                "name": "News Feed",
                "description": "News and updates feed"
            },
            {
                "type": WidgetType.COLLABORATION.value,
                "name": "Collaboration",
                "description": "Team collaboration tools"
            },
            {
                "type": WidgetType.LEARNING_PROGRESS.value,
                "name": "Learning Progress",
                "description": "Educational progress tracking"
            },
            {
                "type": WidgetType.PROJECT_STATUS.value,
                "name": "Project Status",
                "description": "Project management and status"
            },
            {
                "type": WidgetType.SYSTEM_STATUS.value,
                "name": "System Status",
                "description": "System health and monitoring"
            },
            {
                "type": WidgetType.CUSTOM_WIDGET.value,
                "name": "Custom Widget",
                "description": "User-defined custom widget"
            }
        ]
        
        return widget_types
        
    except Exception as e:
        logger.error(f"Error getting available widget types: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get available widget types: {str(e)}"
        )

@router.get("/layouts/available", response_model=List[Dict[str, str]])
async def get_available_layout_types() -> List[Dict[str, str]]:
    """
    Get list of available layout types.
    
    Returns all supported layout types with descriptions for
    dashboard structure and organization options.
    """
    try:
        layout_types = [
            {
                "type": LayoutType.GRID.value,
                "name": "Grid Layout",
                "description": "Traditional grid-based widget arrangement"
            },
            {
                "type": LayoutType.KANBAN.value,
                "name": "Kanban Layout",
                "description": "Column-based kanban-style organization"
            },
            {
                "type": LayoutType.TIMELINE.value,
                "name": "Timeline Layout",
                "description": "Chronological timeline-based layout"
            },
            {
                "type": LayoutType.FOCUS.value,
                "name": "Focus Layout",
                "description": "Single-focus minimal layout for concentration"
            },
            {
                "type": LayoutType.COMPACT.value,
                "name": "Compact Layout",
                "description": "Dense information display for power users"
            },
            {
                "type": LayoutType.VISUAL.value,
                "name": "Visual Layout",
                "description": "Chart and visualization-heavy layout"
            }
        ]
        
        return layout_types
        
    except Exception as e:
        logger.error(f"Error getting available layout types: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get available layout types: {str(e)}"
        )

@router.post("/{dashboard_id}/widgets", response_model=Dict[str, Any])
async def add_widget_to_dashboard(dashboard_id: str, widget_config: WidgetConfigModel) -> Dict[str, Any]:
    """
    Add a new widget to a dashboard.
    
    Dynamically adds a widget to the specified dashboard layout
    with intelligent positioning and size optimization.
    """
    try:
        dashboard = await dashboard_manager.get_dashboard(dashboard_id)
        if not dashboard:
            raise HTTPException(
                status_code=404,
                detail=f"Dashboard {dashboard_id} not found"
            )
        
        # Convert widget config
        new_widget = WidgetConfig(
            widget_id=widget_config.widget_id,
            widget_type=WidgetType(widget_config.widget_type),
            title=widget_config.title,
            size=WidgetSize(widget_config.size),
            position=widget_config.position,
            settings=widget_config.settings,
            is_visible=widget_config.is_visible,
            is_moveable=widget_config.is_moveable,
            is_resizable=widget_config.is_resizable,
            refresh_interval=widget_config.refresh_interval,
            permissions=widget_config.permissions
        )
        
        # Add widget to active layout
        active_layout = next(
            (layout for layout in dashboard.layouts if layout.layout_id == dashboard.active_layout),
            dashboard.layouts[0] if dashboard.layouts else None
        )
        
        if not active_layout:
            raise HTTPException(
                status_code=400,
                detail="No active layout found"
            )
        
        active_layout.widgets.append(new_widget)
        active_layout.updated_at = datetime.utcnow().isoformat()
        
        # Update dashboard
        await dashboard_manager.update_dashboard(dashboard_id, {
            'layouts': dashboard.layouts
        })
        
        return {
            'status': 'success',
            'widget_added': widget_config.widget_id,
            'layout_updated': active_layout.layout_id,
            'timestamp': active_layout.updated_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding widget to dashboard: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add widget: {str(e)}"
        )

@router.delete("/{dashboard_id}/widgets/{widget_id}", response_model=Dict[str, Any])
async def remove_widget_from_dashboard(dashboard_id: str, widget_id: str) -> Dict[str, Any]:
    """
    Remove a widget from a dashboard.
    
    Removes the specified widget from the dashboard layout
    and reorganizes remaining widgets if necessary.
    """
    try:
        dashboard = await dashboard_manager.get_dashboard(dashboard_id)
        if not dashboard:
            raise HTTPException(
                status_code=404,
                detail=f"Dashboard {dashboard_id} not found"
            )
        
        # Find and remove widget from active layout
        active_layout = next(
            (layout for layout in dashboard.layouts if layout.layout_id == dashboard.active_layout),
            dashboard.layouts[0] if dashboard.layouts else None
        )
        
        if not active_layout:
            raise HTTPException(
                status_code=400,
                detail="No active layout found"
            )
        
        # Remove widget
        original_count = len(active_layout.widgets)
        active_layout.widgets = [
            widget for widget in active_layout.widgets 
            if widget.widget_id != widget_id
        ]
        
        if len(active_layout.widgets) == original_count:
            raise HTTPException(
                status_code=404,
                detail=f"Widget {widget_id} not found in dashboard"
            )
        
        active_layout.updated_at = datetime.utcnow().isoformat()
        
        # Update dashboard
        await dashboard_manager.update_dashboard(dashboard_id, {
            'layouts': dashboard.layouts
        })
        
        return {
            'status': 'success',
            'widget_removed': widget_id,
            'layout_updated': active_layout.layout_id,
            'timestamp': active_layout.updated_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing widget from dashboard: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to remove widget: {str(e)}"
        )

@router.get("/health", response_model=Dict[str, Any])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for the personalized dashboard service.
    
    Returns service status and basic diagnostic information.
    """
    try:
        dashboard_count = len(dashboard_manager.dashboards)
        usage_tracked_users = len(dashboard_manager.usage_tracker)
        
        return {
            'status': 'healthy',
            'service': 'personalized-dashboards',
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': {
                'total_dashboards': dashboard_count,
                'users_with_usage_data': usage_tracked_users,
                'available_roles': len(list(DashboardRole)),
                'available_widget_types': len(list(WidgetType)),
                'available_layout_types': len(list(LayoutType))
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            'status': 'unhealthy',
            'service': 'personalized-dashboards',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }

# Helper Functions

def _convert_dashboard_to_model(dashboard: UserDashboard) -> UserDashboardModel:
    """Convert UserDashboard to UserDashboardModel"""
    try:
        # Convert layouts
        layout_models = []
        for layout in dashboard.layouts:
            # Convert widgets
            widget_models = []
            for widget in layout.widgets:
                widget_model = WidgetConfigModel(
                    widget_id=widget.widget_id,
                    widget_type=widget.widget_type.value,
                    title=widget.title,
                    size=widget.size.value,
                    position=widget.position,
                    settings=widget.settings,
                    is_visible=widget.is_visible,
                    is_moveable=widget.is_moveable,
                    is_resizable=widget.is_resizable,
                    refresh_interval=widget.refresh_interval,
                    permissions=widget.permissions
                )
                widget_models.append(widget_model)
            
            # Create layout model
            layout_model = DashboardLayoutModel(
                layout_id=layout.layout_id,
                name=layout.name,
                layout_type=layout.layout_type.value,
                columns=layout.columns,
                rows=layout.rows,
                widgets=widget_models,
                theme=layout.theme,
                is_responsive=layout.is_responsive,
                created_at=layout.created_at,
                updated_at=layout.updated_at
            )
            layout_models.append(layout_model)
        
        # Create dashboard model
        return UserDashboardModel(
            user_id=dashboard.user_id,
            dashboard_id=dashboard.dashboard_id,
            role=dashboard.role.value,
            active_layout=dashboard.active_layout,
            layouts=layout_models,
            preferences=dashboard.preferences,
            usage_stats=dashboard.usage_stats,
            personalization_level=dashboard.personalization_level,
            created_at=dashboard.created_at,
            last_accessed=dashboard.last_accessed
        )
        
    except Exception as e:
        logger.error(f"Error converting dashboard to model: {e}")
        raise

# Export router
__all__ = ['router']
