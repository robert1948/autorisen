"""
Preference Management API Routes
Handles user preferences, settings, and customization options
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, validator
import logging

from ..database import get_db
from ..auth.auth_enhanced import get_current_user
from ..models.user import User

logger = logging.getLogger(__name__)

# Pydantic models for request/response
class PreferenceValue(BaseModel):
    value: Any
    data_type: Optional[str] = None

class PreferencesUpdate(BaseModel):
    preferences: Dict[str, Dict[str, PreferenceValue]]

class PreferenceExport(BaseModel):
    format: str = "json"
    include_defaults: bool = True

class PreferenceImport(BaseModel):
    preferences_data: Dict[str, Any]
    overwrite_existing: bool = False

router = APIRouter(
    prefix="/api/v1/preferences",
    tags=["preferences"],
    responses={404: {"description": "Not found"}}
)

# Initialize preference manager - will be injected via dependency
def get_preference_manager(db: Session = Depends(get_db)):
    """Get preference manager instance"""
    try:
        # Import here to avoid circular imports
        from ..services.preference_management import PreferenceManager
        import redis
        
        # Initialize Redis client (you may want to configure this via environment)
        redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        return PreferenceManager(db, redis_client)
    except Exception as e:
        logger.error(f"Failed to initialize preference manager: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Preference service unavailable"
        )

@router.get("/")
async def get_user_preferences(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    pref_manager = Depends(get_preference_manager)
):
    """
    Get user preferences
    
    - **category**: Optional category filter (general, ai_behavior, interface, etc.)
    - Returns all preferences or filtered by category
    """
    try:
        preferences = await pref_manager.get_user_preferences(current_user.id, category)
        
        return {
            "success": True,
            "user_id": current_user.id,
            "category_filter": category,
            "preferences": preferences,
            "total_categories": len(preferences),
            "timestamp": "2025-07-26"
        }
    except Exception as e:
        logger.error(f"Error getting preferences for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve preferences: {str(e)}"
        )

@router.post("/")
async def set_user_preferences(
    preferences_update: PreferencesUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    pref_manager = Depends(get_preference_manager)
):
    """
    Set multiple user preferences
    
    - **preferences**: Nested dictionary of category -> key -> {value, data_type}
    - Updates multiple preferences atomically
    """
    try:
        # Convert Pydantic model to dict format expected by service
        preferences_dict = {}
        for category, category_prefs in preferences_update.preferences.items():
            preferences_dict[category] = {}
            for key, pref_value in category_prefs.items():
                preferences_dict[category][key] = {
                    "value": pref_value.value,
                    "data_type": pref_value.data_type
                }
        
        results = await pref_manager.set_multiple_preferences(current_user.id, preferences_dict)
        
        # Count successful vs failed updates
        successful = sum(1 for success in results.values() if success)
        failed = len(results) - successful
        
        # Background task: Log preference changes for analytics
        background_tasks.add_task(
            log_preference_changes,
            current_user.id,
            preferences_dict,
            results
        )
        
        return {
            "success": failed == 0,
            "user_id": current_user.id,
            "results": results,
            "summary": {
                "total_preferences": len(results),
                "successful_updates": successful,
                "failed_updates": failed,
                "success_rate": f"{(successful/len(results)*100):.1f}%" if results else "0%"
            },
            "timestamp": "2025-07-26"
        }
    except Exception as e:
        logger.error(f"Error setting preferences for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preferences: {str(e)}"
        )

@router.put("/{category}/{key}")
async def set_single_preference(
    category: str,
    key: str,
    preference_value: PreferenceValue,
    current_user: User = Depends(get_current_user),
    pref_manager = Depends(get_preference_manager)
):
    """
    Set a single preference value
    
    - **category**: Preference category (general, ai_behavior, interface, etc.)
    - **key**: Preference key within the category
    - **value**: New preference value
    - **data_type**: Optional data type specification
    """
    try:
        success = await pref_manager.set_user_preference(
            current_user.id,
            category,
            key,
            preference_value.value,
            preference_value.data_type
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to set preference {category}.{key}"
            )
        
        return {
            "success": True,
            "user_id": current_user.id,
            "preference": {
                "category": category,
                "key": key,
                "value": preference_value.value,
                "data_type": preference_value.data_type
            },
            "message": f"Preference {category}.{key} updated successfully",
            "timestamp": "2025-07-26"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting preference {category}.{key} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preference: {str(e)}"
        )

@router.delete("/{category}")
async def reset_category_preferences(
    category: str,
    current_user: User = Depends(get_current_user),
    pref_manager = Depends(get_preference_manager)
):
    """
    Reset preferences in a category to defaults
    
    - **category**: Category to reset (or "all" for all categories)
    """
    try:
        category_filter = None if category.lower() == "all" else category
        
        success = await pref_manager.reset_to_defaults(current_user.id, category_filter)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to reset preferences for category: {category}"
            )
        
        return {
            "success": True,
            "user_id": current_user.id,
            "reset_category": category,
            "message": f"Preferences reset to defaults for: {category}",
            "timestamp": "2025-07-26"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting preferences for user {current_user.id}, category {category}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset preferences: {str(e)}"
        )

@router.get("/templates")
async def get_preference_templates(
    category: Optional[str] = None,
    pref_manager = Depends(get_preference_manager)
):
    """
    Get preference templates (available options and defaults)
    
    - **category**: Optional category filter
    - Returns template information for UI generation
    """
    try:
        templates = await pref_manager.get_preference_templates(category)
        
        # Group templates by category for easier frontend consumption
        templates_by_category = {}
        for template in templates:
            cat = template["category"]
            if cat not in templates_by_category:
                templates_by_category[cat] = []
            templates_by_category[cat].append(template)
        
        return {
            "success": True,
            "category_filter": category,
            "templates_by_category": templates_by_category,
            "total_templates": len(templates),
            "available_categories": list(templates_by_category.keys()),
            "timestamp": "2025-07-26"
        }
    except Exception as e:
        logger.error(f"Error getting preference templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve preference templates: {str(e)}"
        )

@router.post("/export")
async def export_user_preferences(
    export_config: PreferenceExport,
    current_user: User = Depends(get_current_user),
    pref_manager = Depends(get_preference_manager)
):
    """
    Export user preferences for backup or migration
    
    - **format**: Export format (currently supports "json")
    - **include_defaults**: Whether to include default values
    """
    try:
        if export_config.format.lower() != "json":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only JSON format is currently supported"
            )
        
        exported_data = await pref_manager.export_user_preferences(current_user.id)
        
        return {
            "success": True,
            "user_id": current_user.id,
            "export_format": export_config.format,
            "exported_data": exported_data,
            "export_metadata": {
                "total_categories": len(exported_data.get("preferences", {})),
                "export_timestamp": exported_data.get("exported_at"),
                "include_defaults": export_config.include_defaults
            },
            "timestamp": "2025-07-26"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting preferences for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export preferences: {str(e)}"
        )

@router.post("/import")
async def import_user_preferences(
    import_data: PreferenceImport,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    pref_manager = Depends(get_preference_manager)
):
    """
    Import user preferences from backup
    
    - **preferences_data**: Exported preference data
    - **overwrite_existing**: Whether to overwrite existing preferences
    """
    try:
        if not import_data.preferences_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No preferences data provided"
            )
        
        # If not overwriting, we could merge instead of replace
        if not import_data.overwrite_existing:
            # For now, we'll just import - you could add merge logic here
            pass
        
        success = await pref_manager.import_user_preferences(
            current_user.id,
            import_data.preferences_data
        )
        
        # Background task: Log import activity
        background_tasks.add_task(
            log_preference_import,
            current_user.id,
            success,
            len(import_data.preferences_data.get("preferences", {}))
        )
        
        return {
            "success": success,
            "user_id": current_user.id,
            "import_success": success,
            "imported_categories": len(import_data.preferences_data.get("preferences", {})),
            "overwrite_mode": import_data.overwrite_existing,
            "message": "Preferences imported successfully" if success else "Partial import completed",
            "timestamp": "2025-07-26"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing preferences for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import preferences: {str(e)}"
        )

@router.get("/stats")
async def get_preference_statistics(
    current_user: User = Depends(get_current_user),
    pref_manager = Depends(get_preference_manager)
):
    """
    Get preference usage statistics for the current user
    """
    try:
        # Get current preferences
        preferences = await pref_manager.get_user_preferences(current_user.id)
        
        # Calculate statistics
        stats = {
            "total_categories": len(preferences),
            "total_preferences": sum(len(cat_prefs) for cat_prefs in preferences.values()),
            "categories_configured": [cat for cat in preferences.keys()],
            "customization_level": "high" if len(preferences) > 5 else "medium" if len(preferences) > 2 else "low",
            "last_updated": max(
                (pref.get("updated_at", "2025-07-26") for cat_prefs in preferences.values() for pref in cat_prefs.values()),
                default="2025-07-26"
            )
        }
        
        return {
            "success": True,
            "user_id": current_user.id,
            "statistics": stats,
            "timestamp": "2025-07-26"
        }
    except Exception as e:
        logger.error(f"Error getting preference statistics for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve preference statistics: {str(e)}"
        )

# Background task functions
async def log_preference_changes(user_id: str, preferences: Dict, results: Dict):
    """Log preference changes for analytics"""
    try:
        # This would integrate with your analytics system
        logger.info(f"User {user_id} updated {len(preferences)} preferences")
    except Exception as e:
        logger.error(f"Failed to log preference changes: {e}")

async def log_preference_import(user_id: str, success: bool, category_count: int):
    """Log preference import activity"""
    try:
        logger.info(f"User {user_id} imported {category_count} preference categories, success: {success}")
    except Exception as e:
        logger.error(f"Failed to log preference import: {e}")

# Health check endpoint for preference service
@router.get("/health")
async def preference_service_health(
    pref_manager = Depends(get_preference_manager)
):
    """Health check for preference management service"""
    try:
        # Test basic functionality
        templates = await pref_manager.get_preference_templates()
        
        return {
            "service": "preference_management",
            "status": "healthy",
            "version": "1.0.0",
            "features": {
                "get_preferences": "available",
                "set_preferences": "available",
                "templates": "available",
                "export_import": "available",
                "reset_to_defaults": "available"
            },
            "statistics": {
                "available_templates": len(templates),
                "categories_available": len(set(t["category"] for t in templates))
            },
            "timestamp": "2025-07-26"
        }
    except Exception as e:
        return {
            "service": "preference_management",
            "status": "degraded",
            "error": str(e),
            "timestamp": "2025-07-26"
        }