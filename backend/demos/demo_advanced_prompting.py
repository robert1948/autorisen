"""
Task 2.1.5: Advanced Prompting Templates - Standalone Test Demo
==============================================================

Standalone demonstration and validation of the advanced prompting system
without full app dependencies.
"""

import asyncio
import logging
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

# Import our service
from app.services.advanced_prompting_service import (
    AdvancedPromptingService,
    PromptTemplate,
    PromptGenerationRequest,
    PromptCategory,
    PromptRole,
    PromptComplexity,
    TemplateVersion
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_advanced_prompting():
    """Comprehensive demonstration of advanced prompting capabilities"""
    
    print("🚀 Advanced Prompting Templates System Demo")
    print("=" * 60)
    
    # Initialize service with mocked dependencies
    service = AdvancedPromptingService()
    
    try:
        print("\n📋 1. Service Initialization")
        print("-" * 30)
        
        # Test service initialization
        templates = await service.list_templates()
        print(f"✅ Service initialized with {len(templates)} default templates")
        
        # Display default templates
        for template in templates[:3]:  # Show first 3
            print(f"   • {template.name} ({template.category.value}/{template.role.value})")
        
        print("\n🎨 2. Custom Template Creation")
        print("-" * 30)
        
        # Create a custom template
        custom_template = await service.create_custom_template(
            name="Python Code Reviewer",
            description="Template for Python code review and optimization suggestions",
            category=PromptCategory.CODE_ASSISTANCE,
            role=PromptRole.EXPERT,
            complexity=PromptComplexity.ADVANCED,
            template_content="""
As an expert Python developer, I'll review your {{code_type}} code:

{{code_snippet}}

I'll analyze this code for:
- Code quality and best practices
- Performance optimizations
- Security considerations
- Pythonic improvements

{% if experience_level == 'beginner' %}
I'll provide detailed explanations for each suggestion.
{% else %}
I'll focus on advanced optimization techniques.
{% endif %}
            """.strip(),
            variables=["code_type", "code_snippet", "experience_level"],
            created_by="demo_user",
            tags=["python", "code-review", "optimization"]
        )
        
        print(f"✅ Created custom template: '{custom_template.name}'")
        print(f"   Template ID: {custom_template.template_id}")
        print(f"   Variables: {custom_template.variables}")
        
        print("\n⚡ 3. Template Filtering")
        print("-" * 30)
        
        # Test filtering
        code_templates = await service.list_templates(category=PromptCategory.CODE_ASSISTANCE)
        print(f"✅ Found {len(code_templates)} code assistance templates")
        
        expert_templates = await service.list_templates(role=PromptRole.EXPERT)
        print(f"✅ Found {len(expert_templates)} expert-level templates")
        
        print("\n🔄 4. Prompt Generation")
        print("-" * 30)
        
        # Generate a prompt from our custom template
        generation_request = PromptGenerationRequest(
            template_id=custom_template.template_id,
            user_id="demo_user",
            context_variables={
                "code_type": "function",
                "code_snippet": "def calculate_total(items):\n    total = 0\n    for item in items:\n        total = total + item\n    return total",
                "experience_level": "intermediate"
            },
            personalization_enabled=False  # Disable to avoid dependency issues
        )
        
        generated_prompt = await service.generate_prompt(generation_request)
        
        print("✅ Generated personalized prompt:")
        print("   " + "─" * 50)
        print("   " + generated_prompt.prompt_content.replace("\n", "\n   "))
        print("   " + "─" * 50)
        print(f"   Variables used: {generated_prompt.variables_substituted}")
        
        print("\n📊 5. Template Performance Tracking")
        print("-" * 30)
        
        # Simulate performance feedback
        await service.update_template_performance(
            template_id=custom_template.template_id,
            success=True,
            user_rating=4.8,
            response_time_ms=350
        )
        
        print("✅ Updated template performance metrics")
        
        # Get updated template
        updated_template = service.templates[custom_template.template_id]
        print(f"   Usage count: {updated_template.usage_count}")
        print(f"   Success rate: {updated_template.success_rate:.2%}")
        print(f"   Effectiveness score: {updated_template.effectiveness_score:.3f}")
        
        print("\n📈 6. Analytics Dashboard")
        print("-" * 30)
        
        analytics = await service.get_template_analytics()
        
        print("✅ Template Analytics:")
        print(f"   Total templates: {analytics['overview']['total_templates']}")
        print(f"   Average effectiveness: {analytics['overview']['avg_effectiveness']:.3f}")
        print(f"   Total usage: {analytics['overview']['total_usage']}")
        
        print("\n   Category Distribution:")
        for category, count in analytics['category_distribution'].items():
            if isinstance(count, (int, float)) and count > 0:
                print(f"     • {category}: {count}")
        
        print("\n   Role Distribution:")
        active_roles = {}
        for role, count in analytics['role_distribution'].items():
            if isinstance(count, (int, float)) and count > 0:
                active_roles[role] = count
        
        for role, count in list(active_roles.items())[:5]:  # Show top 5
            print(f"     • {role}: {count}")
        
        print("\n🎯 7. Complex Jinja2 Template Demo")
        print("-" * 30)
        
        # Create a complex template with conditionals and loops
        complex_template = await service.create_custom_template(
            name="Learning Path Generator",
            description="Generates personalized learning paths",
            category=PromptCategory.EDUCATIONAL,
            role=PromptRole.TEACHER,
            complexity=PromptComplexity.ADVANCED,
            template_content="""
Welcome {{student_name}}! 

{% if skill_level == 'beginner' %}
Let's start your {{subject}} journey with the fundamentals:
{% elif skill_level == 'intermediate' %}
Ready to advance your {{subject}} skills? Here's your path:
{% else %}
Time to master {{subject}}! Your advanced curriculum:
{% endif %}

{% for week, topics in learning_plan.items() %}
Week {{week}}:
{% for topic in topics %}
  • {{topic}}
{% endfor %}
{% endfor %}

{% if include_projects %}
Hands-on Projects:
{% for project in projects %}
  🔨 {{project}}
{% endfor %}
{% endif %}

Good luck with your learning journey!
            """.strip(),
            variables=["student_name", "subject", "skill_level", "learning_plan", "include_projects", "projects"],
            created_by="demo_user",
            tags=["education", "learning-path", "personalized"]
        )
        
        # Generate from complex template
        complex_request = PromptGenerationRequest(
            template_id=complex_template.template_id,
            user_id="demo_user",
            context_variables={
                "student_name": "Alex",
                "subject": "Machine Learning",
                "skill_level": "intermediate",
                "learning_plan": {
                    "1": ["Linear Regression", "Logistic Regression"],
                    "2": ["Decision Trees", "Random Forest"],
                    "3": ["Neural Networks", "Deep Learning"]
                },
                "include_projects": True,
                "projects": ["House Price Prediction", "Image Classification", "Sentiment Analysis"]
            },
            personalization_enabled=False
        )
        
        complex_result = await service.generate_prompt(complex_request)
        
        print("✅ Complex template generation:")
        print("   " + "─" * 50)
        print("   " + complex_result.prompt_content.replace("\n", "\n   "))
        print("   " + "─" * 50)
        
        print("\n🏆 8. System Validation Summary")
        print("-" * 30)
        
        final_templates = await service.list_templates()
        total_custom = len([t for t in final_templates if t.created_by == "demo_user"])
        
        print(f"✅ Total templates: {len(final_templates)}")
        print(f"✅ Custom templates created: {total_custom}")
        print(f"✅ Default templates: {len(final_templates) - total_custom}")
        print(f"✅ Template categories: {len(set(t.category for t in final_templates))}")
        print(f"✅ Template roles: {len(set(t.role for t in final_templates))}")
        
        print("\n🎉 Advanced Prompting System Validation Complete!")
        print("   • Template management: ✅")
        print("   • Jinja2 rendering: ✅")
        print("   • Performance tracking: ✅")
        print("   • Analytics generation: ✅")
        print("   • Complex templating: ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logger.exception("Demo execution failed")
        return False


if __name__ == "__main__":
    # Run the demo
    success = asyncio.run(demo_advanced_prompting())
    
    if success:
        print("\n🌟 Task 2.1.5: Advanced Prompting Templates - VALIDATION SUCCESSFUL")
        exit(0)
    else:
        print("\n💥 Task 2.1.5: Advanced Prompting Templates - VALIDATION FAILED")
        exit(1)
