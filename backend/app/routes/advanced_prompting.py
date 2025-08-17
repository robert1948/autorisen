"""
Task 2.1.5: Advanced Prompting Templates API Routes
==================================================

API endpoints for managing and using advanced prompt templates:
- Template library management
- Prompt generation from templates
- Template performance analytics
- Custom template creation
- A/B testing support
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from app.services.advanced_prompting_service import (
    get_prompting_service,
    PromptTemplate,
    PromptGenerationRequest,
    GeneratedPrompt,
    PromptCategory,
    PromptRole,
    PromptComplexity,
    TemplateVersion
)
from app.dependencies import get_current_user
# Import User directly to avoid circular import issues
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/prompting", tags=["Advanced Prompting"])


class TemplateResponse(BaseModel):
    """Response model for prompt templates"""
    template_id: str
    name: str
    description: str
    category: str
    role: str
    complexity: str
    version: str
    template_content: str
    variables: List[str]
    requirements: Dict[str, Any]
    effectiveness_score: float
    usage_count: int
    success_rate: float
    created_at: str
    updated_at: str
    created_by: str
    tags: List[str]
    language: str


class GeneratePromptRequest(BaseModel):
    """Request model for prompt generation"""
    template_id: str = Field(..., description="ID of the template to use")
    context_variables: Optional[Dict[str, Any]] = Field(None, description="Variables to substitute in template")
    personalization_enabled: bool = Field(True, description="Enable personalization")
    target_complexity: Optional[str] = Field(None, description="Target complexity level")
    preferred_role: Optional[str] = Field(None, description="Preferred AI role")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")


class GeneratePromptResponse(BaseModel):
    """Response model for generated prompts"""
    prompt_content: str
    template_used: str
    variables_substituted: Dict[str, Any]
    personalization_applied: bool
    complexity_level: str
    role_used: str
    generation_metadata: Dict[str, Any]
    generated_at: str


class CreateTemplateRequest(BaseModel):
    """Request model for creating custom templates"""
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    category: str = Field(..., description="Template category")
    role: str = Field(..., description="AI role")
    complexity: str = Field(..., description="Complexity level")
    template_content: str = Field(..., description="Template content with Jinja2 variables")
    variables: List[str] = Field(..., description="List of variables used in template")
    tags: Optional[List[str]] = Field(None, description="Template tags")


class TemplatePerformanceRequest(BaseModel):
    """Request model for updating template performance"""
    success: bool = Field(..., description="Whether the template usage was successful")
    user_rating: Optional[float] = Field(None, ge=1.0, le=5.0, description="User rating (1-5)")
    response_time_ms: Optional[int] = Field(None, description="Response time in milliseconds")


@router.get("/templates", response_model=List[TemplateResponse])
async def list_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    role: Optional[str] = Query(None, description="Filter by role"),
    complexity: Optional[str] = Query(None, description="Filter by complexity"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    current_user: User = Depends(get_current_user)
):
    """List available prompt templates with optional filtering"""
    try:
        prompting_service = await get_prompting_service()
        
        # Parse filters
        category_filter = PromptCategory(category) if category else None
        role_filter = PromptRole(role) if role else None
        complexity_filter = PromptComplexity(complexity) if complexity else None
        tags_filter = tags.split(',') if tags else None
        
        # Get filtered templates
        templates = await prompting_service.list_templates(
            category=category_filter,
            role=role_filter,
            complexity=complexity_filter,
            tags=tags_filter
        )
        
        return [
            TemplateResponse(
                template_id=template.template_id,
                name=template.name,
                description=template.description,
                category=template.category.value,
                role=template.role.value,
                complexity=template.complexity.value,
                version=template.version.value,
                template_content=template.template_content,
                variables=template.variables,
                requirements=template.requirements,
                effectiveness_score=template.effectiveness_score,
                usage_count=template.usage_count,
                success_rate=template.success_rate,
                created_at=template.created_at.isoformat(),
                updated_at=template.updated_at.isoformat(),
                created_by=template.created_by,
                tags=template.tags,
                language=template.language
            )
            for template in templates
        ]
        
    except Exception as e:
        logger.error(f"Failed to list templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve templates")


@router.get("/templates/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific template by ID"""
    try:
        prompting_service = await get_prompting_service()
        template = await prompting_service.get_template(template_id)
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return TemplateResponse(
            template_id=template.template_id,
            name=template.name,
            description=template.description,
            category=template.category.value,
            role=template.role.value,
            complexity=template.complexity.value,
            version=template.version.value,
            template_content=template.template_content,
            variables=template.variables,
            requirements=template.requirements,
            effectiveness_score=template.effectiveness_score,
            usage_count=template.usage_count,
            success_rate=template.success_rate,
            created_at=template.created_at.isoformat(),
            updated_at=template.updated_at.isoformat(),
            created_by=template.created_by,
            tags=template.tags,
            language=template.language
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get template {template_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve template")


@router.post("/generate", response_model=GeneratePromptResponse)
async def generate_prompt(
    request: GeneratePromptRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate a personalized prompt from a template"""
    try:
        prompting_service = await get_prompting_service()
        
        # Parse complexity and role if provided
        target_complexity = None
        if request.target_complexity:
            try:
                target_complexity = PromptComplexity(request.target_complexity)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid complexity level")
        
        preferred_role = None
        if request.preferred_role:
            try:
                preferred_role = PromptRole(request.preferred_role)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid role")
        
        # Create generation request
        generation_request = PromptGenerationRequest(
            template_id=request.template_id,
            user_id=str(current_user.id),
            context_variables=request.context_variables,
            personalization_enabled=request.personalization_enabled,
            target_complexity=target_complexity,
            preferred_role=preferred_role,
            conversation_id=request.conversation_id
        )
        
        # Generate prompt
        result = await prompting_service.generate_prompt(generation_request)
        
        return GeneratePromptResponse(
            prompt_content=result.prompt_content,
            template_used=result.template_used,
            variables_substituted=result.variables_substituted,
            personalization_applied=result.personalization_applied,
            complexity_level=result.complexity_level.value,
            role_used=result.role_used.value,
            generation_metadata=result.generation_metadata,
            generated_at=result.generated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate prompt: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate prompt")


@router.post("/templates", response_model=TemplateResponse)
async def create_custom_template(
    request: CreateTemplateRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new custom template"""
    try:
        prompting_service = await get_prompting_service()
        
        # Parse enums
        try:
            category = PromptCategory(request.category)
            role = PromptRole(request.role)
            complexity = PromptComplexity(request.complexity)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid enum value: {e}")
        
        # Create template
        template = await prompting_service.create_custom_template(
            name=request.name,
            description=request.description,
            category=category,
            role=role,
            complexity=complexity,
            template_content=request.template_content,
            variables=request.variables,
            created_by=str(current_user.id),
            tags=request.tags
        )
        
        return TemplateResponse(
            template_id=template.template_id,
            name=template.name,
            description=template.description,
            category=template.category.value,
            role=template.role.value,
            complexity=template.complexity.value,
            version=template.version.value,
            template_content=template.template_content,
            variables=template.variables,
            requirements=template.requirements,
            effectiveness_score=template.effectiveness_score,
            usage_count=template.usage_count,
            success_rate=template.success_rate,
            created_at=template.created_at.isoformat(),
            updated_at=template.updated_at.isoformat(),
            created_by=template.created_by,
            tags=template.tags,
            language=template.language
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create custom template: {e}")
        raise HTTPException(status_code=500, detail="Failed to create template")


@router.post("/templates/{template_id}/performance")
async def update_template_performance(
    template_id: str,
    request: TemplatePerformanceRequest,
    current_user: User = Depends(get_current_user)
):
    """Update template performance metrics based on usage feedback"""
    try:
        prompting_service = await get_prompting_service()
        
        await prompting_service.update_template_performance(
            template_id=template_id,
            success=request.success,
            user_rating=request.user_rating,
            response_time_ms=request.response_time_ms
        )
        
        return {"status": "success", "message": "Template performance updated"}
        
    except Exception as e:
        logger.error(f"Failed to update template performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to update performance")


@router.get("/categories")
async def get_prompt_categories():
    """Get available prompt categories"""
    return {
        "categories": [
            {"value": cat.value, "name": cat.value.replace("_", " ").title()}
            for cat in PromptCategory
        ]
    }


@router.get("/roles")
async def get_prompt_roles():
    """Get available AI roles"""
    return {
        "roles": [
            {"value": role.value, "name": role.value.title()}
            for role in PromptRole
        ]
    }


@router.get("/complexity-levels")
async def get_complexity_levels():
    """Get available complexity levels"""
    return {
        "complexity_levels": [
            {"value": level.value, "name": level.value.title()}
            for level in PromptComplexity
        ]
    }


@router.get("/analytics")
async def get_template_analytics(current_user: User = Depends(get_current_user)):
    """Get comprehensive template analytics"""
    try:
        prompting_service = await get_prompting_service()
        analytics = await prompting_service.get_template_analytics()
        
        return analytics
        
    except Exception as e:
        logger.error(f"Failed to get template analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")


@router.get("/recommendations")
async def get_template_recommendations(
    category: Optional[str] = Query(None, description="Category for recommendations"),
    limit: int = Query(5, ge=1, le=20, description="Number of recommendations"),
    current_user: User = Depends(get_current_user)
):
    """Get template recommendations based on user preferences and performance"""
    try:
        prompting_service = await get_prompting_service()
        
        # Get user's personalization profile for recommendations
        from app.services.ai_personalization_service import get_personalization_service
        personalization_service = await get_personalization_service()
        
        user_profile = await personalization_service.get_personality_profile(str(current_user.id))
        
        # Filter templates based on category if provided
        category_filter = PromptCategory(category) if category else None
        
        # Get templates
        templates = await prompting_service.list_templates(category=category_filter)
        
        # Score templates based on user preferences and performance
        scored_templates = []
        for template in templates:
            score = template.effectiveness_score
            
            # Boost score based on user preferences
            if user_profile:
                # Prefer templates matching communication style
                if template.role == PromptRole.TEACHER and user_profile.learning_style.value in ['visual', 'kinesthetic']:
                    score += 0.1
                elif template.role == PromptRole.EXPERT and user_profile.expertise_level.value == 'advanced':
                    score += 0.1
                elif template.role == PromptRole.ASSISTANT and user_profile.communication_style.value == 'casual':
                    score += 0.1
                
                # Prefer templates matching complexity
                if template.complexity.value == user_profile.expertise_level.value:
                    score += 0.15
                
                # Prefer templates with relevant tags
                user_topics = [topic.lower() for topic in user_profile.topics_of_interest]
                if any(tag.lower() in user_topics for tag in template.tags):
                    score += 0.1
            
            scored_templates.append((template, score))
        
        # Sort by score and return top recommendations
        scored_templates.sort(key=lambda x: x[1], reverse=True)
        recommendations = scored_templates[:limit]
        
        return {
            "recommendations": [
                {
                    "template_id": template.template_id,
                    "name": template.name,
                    "description": template.description,
                    "category": template.category.value,
                    "role": template.role.value,
                    "complexity": template.complexity.value,
                    "effectiveness_score": template.effectiveness_score,
                    "recommendation_score": score,
                    "tags": template.tags
                }
                for template, score in recommendations
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get template recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")


@router.post("/chat-with-template")
async def chat_with_template(
    template_id: str,
    message: str,
    context_variables: Optional[Dict[str, Any]] = None,
    conversation_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Generate a response using a template and multi-provider AI service"""
    try:
        from app.services.multi_provider_ai_service import MultiProviderAIService
        import uuid
        
        # Initialize services
        prompting_service = await get_prompting_service()
        ai_service = MultiProviderAIService()
        
        # Generate prompt from template
        generation_request = PromptGenerationRequest(
            template_id=template_id,
            user_id=str(current_user.id),
            context_variables=context_variables,
            personalization_enabled=True,
            conversation_id=conversation_id
        )
        
        generated_prompt = await prompting_service.generate_prompt(generation_request)
        
        # Prepare messages for AI service
        messages = [
            {"role": "system", "content": generated_prompt.prompt_content},
            {"role": "user", "content": message}
        ]
        
        # Generate AI response
        conv_id = conversation_id or str(uuid.uuid4())
        ai_response = await ai_service.generate_response(
            messages=messages,
            user_id=str(current_user.id),
            conversation_id=conv_id,
            use_context=True,
            use_personalization=True
        )
        
        # Update template performance (assume success if no error)
        await prompting_service.update_template_performance(
            template_id=template_id,
            success=True,
            response_time_ms=ai_response.response_time_ms
        )
        
        return {
            "response": ai_response.content,
            "template_used": generated_prompt.template_used,
            "model_used": ai_response.model,
            "provider_used": ai_response.provider.value,
            "conversation_id": conv_id,
            "template_metadata": generated_prompt.generation_metadata,
            "response_time_ms": ai_response.response_time_ms,
            "tokens_used": ai_response.usage
        }
        
    except Exception as e:
        logger.error(f"Failed to chat with template: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate response")
