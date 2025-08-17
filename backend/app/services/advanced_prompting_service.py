"""
Task 2.1.5: Advanced Prompting Templates Service
===============================================

Sophisticated prompt template system for AI interactions:
- Dynamic template creation and management
- Context-aware prompt generation
- Role-based prompt customization
- Template versioning and optimization
- A/B testing for prompt effectiveness
- Industry-specific prompt libraries
- Multi-language prompt support
"""

import logging
import json
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import re
from jinja2 import Template, Environment, BaseLoader

# Import personalization service for template customization
from app.services.ai_personalization_service import get_personalization_service, UserPersonalityProfile
from app.services.conversation_context_service import get_context_service, ContextType

logger = logging.getLogger(__name__)


class PromptCategory(str, Enum):
    """Categories of prompt templates"""
    GENERAL_CHAT = "general_chat"
    CODE_ASSISTANCE = "code_assistance"
    CREATIVE_WRITING = "creative_writing"
    EDUCATIONAL = "educational"
    BUSINESS = "business"
    TECHNICAL_SUPPORT = "technical_support"
    DATA_ANALYSIS = "data_analysis"
    RESEARCH = "research"
    BRAINSTORMING = "brainstorming"
    PROBLEM_SOLVING = "problem_solving"


class PromptRole(str, Enum):
    """AI roles for different prompt types"""
    ASSISTANT = "assistant"
    TEACHER = "teacher"
    EXPERT = "expert"
    MENTOR = "mentor"
    ANALYST = "analyst"
    CONSULTANT = "consultant"
    RESEARCHER = "researcher"
    DEVELOPER = "developer"
    WRITER = "writer"
    COACH = "coach"


class PromptComplexity(str, Enum):
    """Complexity levels for prompts"""
    SIMPLE = "simple"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class TemplateVersion(str, Enum):
    """Template versioning for A/B testing"""
    V1 = "v1"
    V2 = "v2"
    V3 = "v3"
    LATEST = "latest"


@dataclass
class PromptTemplate:
    """Advanced prompt template with metadata"""
    template_id: str
    name: str
    description: str
    category: PromptCategory
    role: PromptRole
    complexity: PromptComplexity
    version: TemplateVersion
    template_content: str
    variables: List[str]  # Variables that can be substituted
    requirements: Dict[str, Any]  # Requirements for using this template
    effectiveness_score: float  # Performance metric (0-1)
    usage_count: int
    success_rate: float  # Success rate based on user feedback
    created_at: datetime
    updated_at: datetime
    created_by: str
    tags: List[str]
    language: str = "en"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'template_id': self.template_id,
            'name': self.name,
            'description': self.description,
            'category': self.category.value,
            'role': self.role.value,
            'complexity': self.complexity.value,
            'version': self.version.value,
            'template_content': self.template_content,
            'variables': self.variables,
            'requirements': self.requirements,
            'effectiveness_score': self.effectiveness_score,
            'usage_count': self.usage_count,
            'success_rate': self.success_rate,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': self.created_by,
            'tags': self.tags,
            'language': self.language
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptTemplate':
        """Create from dictionary"""
        return cls(
            template_id=data['template_id'],
            name=data['name'],
            description=data['description'],
            category=PromptCategory(data['category']),
            role=PromptRole(data['role']),
            complexity=PromptComplexity(data['complexity']),
            version=TemplateVersion(data['version']),
            template_content=data['template_content'],
            variables=data['variables'],
            requirements=data['requirements'],
            effectiveness_score=data['effectiveness_score'],
            usage_count=data['usage_count'],
            success_rate=data['success_rate'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            created_by=data['created_by'],
            tags=data['tags'],
            language=data.get('language', 'en')
        )


@dataclass
class PromptGenerationRequest:
    """Request for generating a prompt from template"""
    template_id: str
    user_id: Optional[str] = None
    context_variables: Optional[Dict[str, Any]] = None
    personalization_enabled: bool = True
    target_complexity: Optional[PromptComplexity] = None
    preferred_role: Optional[PromptRole] = None
    conversation_id: Optional[str] = None


@dataclass
class GeneratedPrompt:
    """Result of prompt generation"""
    prompt_content: str
    template_used: str
    variables_substituted: Dict[str, Any]
    personalization_applied: bool
    complexity_level: PromptComplexity
    role_used: PromptRole
    generation_metadata: Dict[str, Any]
    generated_at: datetime


class AdvancedPromptingService:
    """Service for advanced prompt template management and generation"""
    
    def __init__(self):
        self.templates = {}  # In-memory template cache
        self.template_performance = {}  # Template performance tracking
        self.jinja_env = Environment(loader=BaseLoader())
        self.personalization_service = None
        self.context_service = None
        
    async def initialize(self):
        """Initialize the prompting service"""
        self.personalization_service = await get_personalization_service()
        self.context_service = await get_context_service()
        await self._load_default_templates()
        logger.info("Advanced Prompting Service initialized")
    
    async def _load_default_templates(self):
        """Load default prompt templates"""
        default_templates = self._create_default_templates()
        
        for template in default_templates:
            self.templates[template.template_id] = template
            self.template_performance[template.template_id] = {
                'usage_count': 0,
                'success_count': 0,
                'total_rating': 0.0,
                'avg_response_time': 0.0
            }
        
        logger.info(f"Loaded {len(default_templates)} default prompt templates")
    
    def _create_default_templates(self) -> List[PromptTemplate]:
        """Create comprehensive default template library"""
        templates = []
        
        # General Chat Templates
        templates.append(PromptTemplate(
            template_id="general_chat_friendly",
            name="Friendly General Assistant",
            description="Warm, approachable assistant for general conversations",
            category=PromptCategory.GENERAL_CHAT,
            role=PromptRole.ASSISTANT,
            complexity=PromptComplexity.SIMPLE,
            version=TemplateVersion.V1,
            template_content="""You are a helpful and friendly AI assistant named {{ ai_name | default('Assistant') }}. 
You have a warm, approachable personality and enjoy helping users with various questions and tasks.

{% if user_name %}Hello {{ user_name }}! {% endif %}I'm here to help you with whatever you need. 
Whether you have questions, need advice, or just want to chat, I'm ready to assist.

My communication style: {{ communication_style | default('friendly and professional') }}
My expertise areas: {{ expertise_areas | default('general knowledge and problem-solving') }}

How can I help you today?""",
            variables=["ai_name", "user_name", "communication_style", "expertise_areas"],
            requirements={"min_context": 0, "personalization": True},
            effectiveness_score=0.8,
            usage_count=0,
            success_rate=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by="system",
            tags=["friendly", "general", "conversational"]
        ))
        
        # Code Assistance Templates
        templates.append(PromptTemplate(
            template_id="code_assistant_expert",
            name="Expert Code Assistant",
            description="Technical coding assistant for programming tasks",
            category=PromptCategory.CODE_ASSISTANCE,
            role=PromptRole.DEVELOPER,
            complexity=PromptComplexity.ADVANCED,
            version=TemplateVersion.V1,
            template_content="""You are an expert software developer and coding assistant with deep knowledge in {{ programming_languages | default('multiple programming languages') }}.

**Your Expertise:**
- {{ expertise_level | default('Senior') }} level programming experience
- Specialization in: {{ specializations | default('web development, algorithms, and system design') }}
- Code quality focus: {{ quality_focus | default('clean code, best practices, and performance') }}

**Your Approach:**
- Provide clear, well-commented code examples
- Explain the reasoning behind your solutions
- Suggest optimizations and best practices
- Include error handling and edge cases
{% if user_skill_level == 'beginner' %}
- Use simple explanations suitable for beginners
- Break down complex concepts step by step
{% elif user_skill_level == 'advanced' %}
- Assume strong programming background
- Focus on advanced patterns and optimizations
{% endif %}

**Current Task Context:**
{{ task_description | default('General programming assistance needed') }}

Ready to help with your coding challenge!""",
            variables=["programming_languages", "expertise_level", "specializations", "quality_focus", "user_skill_level", "task_description"],
            requirements={"min_context": 1, "domain": "programming"},
            effectiveness_score=0.9,
            usage_count=0,
            success_rate=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by="system",
            tags=["coding", "programming", "technical", "expert"]
        ))
        
        # Educational Templates
        templates.append(PromptTemplate(
            template_id="teacher_patient",
            name="Patient Teacher",
            description="Educational assistant with teaching expertise",
            category=PromptCategory.EDUCATIONAL,
            role=PromptRole.TEACHER,
            complexity=PromptComplexity.INTERMEDIATE,
            version=TemplateVersion.V1,
            template_content="""You are a patient and knowledgeable teacher specializing in {{ subject_area | default('various academic subjects') }}.

**Teaching Philosophy:**
- Every student learns at their own pace
- Questions are always welcome and encouraged
- Learning should be engaging and fun
- Real-world examples make concepts clearer

**Your Teaching Style:**
- Break down complex topics into digestible parts
- Use analogies and examples to illustrate concepts
- Encourage critical thinking and curiosity
- Provide positive reinforcement and constructive feedback

{% if student_level %}
**Student Level:** {{ student_level }}
{% if student_level == 'beginner' %}
I'll start with the fundamentals and build up gradually.
{% elif student_level == 'intermediate' %}
I'll connect new concepts to what you already know.
{% elif student_level == 'advanced' %}
I'll challenge you with deeper analysis and connections.
{% endif %}
{% endif %}

{% if learning_objectives %}
**Today's Learning Goals:**
{% for objective in learning_objectives %}
- {{ objective }}
{% endfor %}
{% endif %}

What would you like to learn about today?""",
            variables=["subject_area", "student_level", "learning_objectives"],
            requirements={"personalization": True, "learning_context": True},
            effectiveness_score=0.85,
            usage_count=0,
            success_rate=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by="system",
            tags=["education", "teaching", "patient", "supportive"]
        ))
        
        # Creative Writing Templates
        templates.append(PromptTemplate(
            template_id="creative_writer_inspiring",
            name="Inspiring Creative Writer",
            description="Creative writing assistant for stories, poems, and content",
            category=PromptCategory.CREATIVE_WRITING,
            role=PromptRole.WRITER,
            complexity=PromptComplexity.INTERMEDIATE,
            version=TemplateVersion.V1,
            template_content="""You are a creative and inspiring writing assistant with a passion for {{ writing_genres | default('storytelling, poetry, and creative expression') }}.

**Creative Philosophy:**
- Every story has the power to move people
- Creativity flourishes with the right inspiration
- Writing is a journey of discovery
- There are no wrong ideas, only different perspectives

**Your Writing Strengths:**
- {{ writing_strengths | default('Character development, world-building, and emotional depth') }}
- Genre expertise: {{ genre_expertise | default('Fantasy, Science Fiction, Literary Fiction') }}
- Style preferences: {{ style_preferences | default('Vivid imagery, compelling dialogue, engaging narratives') }}

**Creative Process:**
{% if project_type %}
**Current Project:** {{ project_type }}
{% endif %}
- Brainstorm ideas collaboratively
- Develop rich characters and settings
- Craft compelling plot structures
- Polish prose for maximum impact

{% if inspiration_sources %}
**Drawing Inspiration From:**
{% for source in inspiration_sources %}
- {{ source }}
{% endfor %}
{% endif %}

Let's create something amazing together! What story are you ready to tell?""",
            variables=["writing_genres", "writing_strengths", "genre_expertise", "style_preferences", "project_type", "inspiration_sources"],
            requirements={"creativity": True, "inspiration": True},
            effectiveness_score=0.82,
            usage_count=0,
            success_rate=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by="system",
            tags=["creative", "writing", "storytelling", "inspiring"]
        ))
        
        # Business Consultant Template
        templates.append(PromptTemplate(
            template_id="business_consultant_strategic",
            name="Strategic Business Consultant",
            description="Professional business advisor for strategic decisions",
            category=PromptCategory.BUSINESS,
            role=PromptRole.CONSULTANT,
            complexity=PromptComplexity.ADVANCED,
            version=TemplateVersion.V1,
            template_content="""You are a strategic business consultant with {{ experience_years | default('15+') }} years of experience in {{ business_domains | default('strategy, operations, and growth') }}.

**Professional Background:**
- Specialization: {{ specializations | default('Strategic planning, market analysis, operational efficiency') }}
- Industry Experience: {{ industries | default('Technology, Healthcare, Finance, Retail') }}
- Methodology: {{ methodology | default('Data-driven analysis with practical implementation focus') }}

**Consulting Approach:**
1. **Understand** the business context and challenges
2. **Analyze** market conditions and competitive landscape
3. **Develop** strategic recommendations with clear rationale
4. **Present** actionable solutions with implementation roadmaps

**Key Strengths:**
- Strategic thinking and market insight
- Financial analysis and ROI evaluation
- Change management and implementation planning
- Stakeholder communication and buy-in

{% if business_context %}
**Current Business Context:**
{{ business_context }}
{% endif %}

{% if specific_challenges %}
**Identified Challenges:**
{% for challenge in specific_challenges %}
- {{ challenge }}
{% endfor %}
{% endif %}

I'm ready to help you navigate your business challenges with strategic insights and practical solutions.""",
            variables=["experience_years", "business_domains", "specializations", "industries", "methodology", "business_context", "specific_challenges"],
            requirements={"business_context": True, "professional": True},
            effectiveness_score=0.88,
            usage_count=0,
            success_rate=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by="system",
            tags=["business", "consulting", "strategy", "professional"]
        ))
        
        # Research Assistant Template
        templates.append(PromptTemplate(
            template_id="research_assistant_thorough",
            name="Thorough Research Assistant",
            description="Academic and professional research support",
            category=PromptCategory.RESEARCH,
            role=PromptRole.RESEARCHER,
            complexity=PromptComplexity.ADVANCED,
            version=TemplateVersion.V1,
            template_content="""You are a meticulous research assistant with expertise in {{ research_domains | default('academic research, data analysis, and literature review') }}.

**Research Methodology:**
- Systematic literature review and source evaluation
- Critical analysis of data and evidence
- Synthesis of findings from multiple sources
- Clear documentation of research process and limitations

**Areas of Expertise:**
- {{ subject_expertise | default('Interdisciplinary research across sciences and humanities') }}
- Research methods: {{ research_methods | default('Qualitative and quantitative analysis') }}
- Data sources: {{ data_sources | default('Academic databases, industry reports, primary research') }}

**Research Standards:**
✓ Evidence-based conclusions
✓ Proper source attribution
✓ Objective analysis and bias recognition
✓ Reproducible methodology
✓ Clear presentation of findings

{% if research_question %}
**Current Research Question:**
{{ research_question }}
{% endif %}

{% if research_scope %}
**Research Scope:**
{{ research_scope }}
{% endif %}

I'm committed to helping you conduct thorough, reliable research that meets the highest academic and professional standards.""",
            variables=["research_domains", "subject_expertise", "research_methods", "data_sources", "research_question", "research_scope"],
            requirements={"academic": True, "thoroughness": True},
            effectiveness_score=0.87,
            usage_count=0,
            success_rate=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by="system",
            tags=["research", "academic", "thorough", "analytical"]
        ))
        
        return templates
    
    async def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Get a specific template by ID"""
        template = self.templates.get(template_id)
        if template:
            # Update usage statistics
            self.template_performance[template_id]['usage_count'] += 1
        return template
    
    async def list_templates(
        self,
        category: Optional[PromptCategory] = None,
        role: Optional[PromptRole] = None,
        complexity: Optional[PromptComplexity] = None,
        tags: Optional[List[str]] = None
    ) -> List[PromptTemplate]:
        """List templates with optional filtering"""
        templates = list(self.templates.values())
        
        if category:
            templates = [t for t in templates if t.category == category]
        
        if role:
            templates = [t for t in templates if t.role == role]
        
        if complexity:
            templates = [t for t in templates if t.complexity == complexity]
        
        if tags:
            templates = [t for t in templates if any(tag in t.tags for tag in tags)]
        
        # Sort by effectiveness score (descending)
        templates.sort(key=lambda t: t.effectiveness_score, reverse=True)
        
        return templates
    
    async def generate_prompt(self, request: PromptGenerationRequest) -> GeneratedPrompt:
        """Generate a personalized prompt from a template"""
        try:
            # Get the template
            template = await self.get_template(request.template_id)
            if not template:
                raise ValueError(f"Template '{request.template_id}' not found")
            
            # Prepare context variables
            context_vars = request.context_variables or {}
            
            # Add personalization if enabled and user provided
            if request.personalization_enabled and request.user_id:
                personalization_context = await self._get_personalization_context(
                    request.user_id,
                    template,
                    request.conversation_id
                )
                context_vars.update(personalization_context)
            
            # Add conversation context if available
            if request.conversation_id and request.user_id:
                conversation_context = await self._get_conversation_context(
                    request.user_id,
                    request.conversation_id
                )
                context_vars.update(conversation_context)
            
            # Adjust template based on preferences
            adjusted_template = await self._adjust_template_for_user(
                template,
                request.user_id,
                request.target_complexity,
                request.preferred_role
            )
            
            # Render the template with Jinja2
            jinja_template = self.jinja_env.from_string(adjusted_template.template_content)
            rendered_prompt = jinja_template.render(**context_vars)
            
            # Clean up the rendered prompt
            cleaned_prompt = self._clean_rendered_prompt(rendered_prompt)
            
            # Create generation result
            result = GeneratedPrompt(
                prompt_content=cleaned_prompt,
                template_used=template.template_id,
                variables_substituted=context_vars,
                personalization_applied=request.personalization_enabled and request.user_id is not None,
                complexity_level=adjusted_template.complexity,
                role_used=adjusted_template.role,
                generation_metadata={
                    'original_template': template.name,
                    'template_version': template.version.value,
                    'personalization_enabled': request.personalization_enabled,
                    'context_variables_count': len(context_vars),
                    'template_effectiveness': template.effectiveness_score
                },
                generated_at=datetime.now()
            )
            
            logger.info(f"Generated prompt from template '{template.template_id}' for user '{request.user_id}'")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate prompt from template '{request.template_id}': {e}")
            raise
    
    async def _get_personalization_context(
        self,
        user_id: str,
        template: PromptTemplate,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get personalization context variables"""
        context = {}
        
        try:
            if self.personalization_service:
                profile = await self.personalization_service.get_personality_profile(user_id)
                if profile:
                    # Map personality profile to template variables
                    context.update({
                        'communication_style': profile.communication_style.value,
                        'user_skill_level': profile.expertise_level.value,
                        'learning_style': profile.learning_style.value,
                        'preferred_response_length': profile.preferred_response_length,
                        'personality_traits': [trait.value for trait in profile.personality_traits],
                        'expertise_areas': profile.topics_of_interest,
                        'learning_objectives': profile.learning_goals
                    })
                    
                    # Customize based on template category
                    if template.category == PromptCategory.CODE_ASSISTANCE:
                        programming_interests = [topic for topic in profile.topics_of_interest 
                                               if any(lang in topic.lower() for lang in ['python', 'javascript', 'java', 'c++', 'programming'])]
                        if programming_interests:
                            context['programming_languages'] = ', '.join(programming_interests)
                        context['expertise_level'] = profile.expertise_level.value.title()
                    
                    elif template.category == PromptCategory.EDUCATIONAL:
                        context['student_level'] = profile.expertise_level.value
                        context['subject_area'] = ', '.join(profile.topics_of_interest[:3]) if profile.topics_of_interest else 'general topics'
                    
                    elif template.category == PromptCategory.CREATIVE_WRITING:
                        creative_interests = [topic for topic in profile.topics_of_interest 
                                            if any(term in topic.lower() for term in ['writing', 'story', 'creative', 'fiction'])]
                        if creative_interests:
                            context['writing_genres'] = ', '.join(creative_interests)
                    
        except Exception as e:
            logger.warning(f"Failed to get personalization context: {e}")
        
        return context
    
    async def _get_conversation_context(self, user_id: str, conversation_id: str) -> Dict[str, Any]:
        """Get conversation context variables"""
        context = {}
        
        try:
            if self.context_service:
                # Get recent conversation history
                history = await self.context_service.get_conversation_history(user_id, limit=5)
                if history:
                    # Extract relevant context
                    recent_topics = []
                    user_questions = []
                    
                    for msg in history:
                        if msg.get('role') == 'user':
                            content = msg.get('content', '')
                            if '?' in content:
                                user_questions.append(content.split('?')[0] + '?')
                    
                    if user_questions:
                        context['recent_questions'] = user_questions[-2:]  # Last 2 questions
                
        except Exception as e:
            logger.warning(f"Failed to get conversation context: {e}")
        
        return context
    
    async def _adjust_template_for_user(
        self,
        template: PromptTemplate,
        user_id: Optional[str],
        target_complexity: Optional[PromptComplexity],
        preferred_role: Optional[PromptRole]
    ) -> PromptTemplate:
        """Adjust template based on user preferences"""
        adjusted_template = template
        
        # Adjust complexity if requested
        if target_complexity and target_complexity != template.complexity:
            # Find alternative template with desired complexity
            alternatives = await self.list_templates(
                category=template.category,
                complexity=target_complexity
            )
            if alternatives:
                adjusted_template = alternatives[0]  # Use the best alternative
        
        # Adjust role if requested
        if preferred_role and preferred_role != template.role:
            # Find alternative template with desired role
            alternatives = await self.list_templates(
                category=template.category,
                role=preferred_role
            )
            if alternatives:
                adjusted_template = alternatives[0]  # Use the best alternative
        
        return adjusted_template
    
    def _clean_rendered_prompt(self, prompt: str) -> str:
        """Clean up the rendered prompt"""
        # Remove excessive whitespace
        prompt = re.sub(r'\n\s*\n\s*\n', '\n\n', prompt)
        
        # Remove leading/trailing whitespace
        prompt = prompt.strip()
        
        # Remove empty list items
        prompt = re.sub(r'\n-\s*\n', '\n', prompt)
        
        return prompt
    
    async def create_custom_template(
        self,
        name: str,
        description: str,
        category: PromptCategory,
        role: PromptRole,
        complexity: PromptComplexity,
        template_content: str,
        variables: List[str],
        created_by: str,
        tags: Optional[List[str]] = None
    ) -> PromptTemplate:
        """Create a new custom template"""
        template_id = f"custom_{hashlib.md5(f'{name}_{created_by}_{datetime.now()}'.encode()).hexdigest()[:8]}"
        
        template = PromptTemplate(
            template_id=template_id,
            name=name,
            description=description,
            category=category,
            role=role,
            complexity=complexity,
            version=TemplateVersion.V1,
            template_content=template_content,
            variables=variables,
            requirements={},
            effectiveness_score=0.5,  # Default score
            usage_count=0,
            success_rate=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=created_by,
            tags=tags or []
        )
        
        # Store template
        self.templates[template_id] = template
        self.template_performance[template_id] = {
            'usage_count': 0,
            'success_count': 0,
            'total_rating': 0.0,
            'avg_response_time': 0.0
        }
        
        logger.info(f"Created custom template '{template_id}' by user '{created_by}'")
        return template
    
    async def update_template_performance(
        self,
        template_id: str,
        success: bool,
        user_rating: Optional[float] = None,
        response_time_ms: Optional[int] = None
    ):
        """Update template performance metrics"""
        if template_id not in self.template_performance:
            return
        
        perf = self.template_performance[template_id]
        
        if success:
            perf['success_count'] += 1
        
        if user_rating is not None:
            perf['total_rating'] += user_rating
            
        if response_time_ms is not None:
            current_avg = perf['avg_response_time']
            count = perf['usage_count']
            perf['avg_response_time'] = (current_avg * count + response_time_ms) / (count + 1)
        
        # Update template effectiveness score
        if template_id in self.templates:
            template = self.templates[template_id]
            if perf['usage_count'] > 0:
                template.success_rate = perf['success_count'] / perf['usage_count']
                if perf['total_rating'] > 0:
                    avg_rating = perf['total_rating'] / perf['success_count'] if perf['success_count'] > 0 else 0
                    template.effectiveness_score = (template.success_rate * 0.7) + (avg_rating / 5.0 * 0.3)
    
    async def get_template_analytics(self) -> Dict[str, Any]:
        """Get comprehensive template analytics"""
        total_templates = len(self.templates)
        total_usage = sum(perf['usage_count'] for perf in self.template_performance.values())
        
        # Category distribution
        category_stats = {}
        for template in self.templates.values():
            cat = template.category.value
            if cat not in category_stats:
                category_stats[cat] = {'count': 0, 'usage': 0, 'avg_effectiveness': 0}
            category_stats[cat]['count'] += 1
            category_stats[cat]['usage'] += self.template_performance[template.template_id]['usage_count']
            category_stats[cat]['avg_effectiveness'] += template.effectiveness_score
        
        # Calculate averages
        for stats in category_stats.values():
            if stats['count'] > 0:
                stats['avg_effectiveness'] /= stats['count']
        
        # Top performing templates
        top_templates = sorted(
            self.templates.values(),
            key=lambda t: t.effectiveness_score,
            reverse=True
        )[:5]
        
        return {
            'overview': {
                'total_templates': total_templates,
                'total_usage': total_usage,
                'avg_effectiveness': sum(t.effectiveness_score for t in self.templates.values()) / total_templates if total_templates > 0 else 0
            },
            'category_distribution': category_stats,
            'top_performing_templates': [
                {
                    'id': t.template_id,
                    'name': t.name,
                    'category': t.category.value,
                    'effectiveness_score': t.effectiveness_score,
                    'usage_count': t.usage_count
                }
                for t in top_templates
            ],
            'role_distribution': {
                role.value: len([t for t in self.templates.values() if t.role == role])
                for role in PromptRole
            }
        }


# Global instance
_prompting_service: Optional[AdvancedPromptingService] = None


async def get_prompting_service() -> AdvancedPromptingService:
    """Get or create the global prompting service instance"""
    global _prompting_service
    
    if _prompting_service is None:
        _prompting_service = AdvancedPromptingService()
        await _prompting_service.initialize()
    
    return _prompting_service


async def initialize_prompting_service():
    """Initialize the prompting service on startup"""
    await get_prompting_service()
    logger.info("✅ Advanced Prompting Service initialized - Task 2.1.5")
