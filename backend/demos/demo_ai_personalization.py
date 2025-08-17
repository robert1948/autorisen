"""
Task 2.1.4: AI Personalization Demo
===================================

Interactive demonstration of the AI personalization system:
- User personality profiling
- Personalized AI interactions
- Learning style adaptation
- Communication style customization
- Real-time personalization insights
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# Import personalization components
from app.services.ai_personalization_service import (
    AIPersonalizationService,
    LearningStyle,
    CommunicationStyle,
    ExpertiseLevel,
    PersonalityTrait
)


class PersonalizationDemo:
    """Interactive demonstration of AI personalization"""
    
    def __init__(self):
        self.personalization_service = None
        self.demo_users = {}
        
    async def initialize(self):
        """Initialize the personalization service"""
        self.personalization_service = AIPersonalizationService()
        await self.personalization_service.initialize()
        print("🧠 AI Personalization Demo initialized")
    
    async def create_demo_users(self):
        """Create demonstration users with different profiles"""
        
        # User 1: Visual Learner, Beginner, Casual
        user1_prefs = {
            'topics_of_interest': ['programming', 'web design'],
            'communication_style': 'casual',
            'preferred_ai_model': 'gpt-4'
        }
        
        # Mock context service for user 1
        self.personalization_service.context_service = MockContextService(user1_prefs)
        
        profile1 = await self.personalization_service.create_personality_profile("demo_user_1")
        self.demo_users["demo_user_1"] = {
            'name': 'Alice (Visual Beginner)',
            'profile': profile1,
            'description': 'Visual learner, beginner level, prefers casual communication'
        }
        
        # User 2: Technical Expert, Professional
        user2_prefs = {
            'topics_of_interest': ['machine learning', 'deep learning', 'ai research', 'neural networks', 'computer vision', 'nlp'],
            'communication_style': 'technical',
            'preferred_ai_model': 'gpt-4'
        }
        
        self.personalization_service.context_service = MockContextService(user2_prefs)
        
        profile2 = await self.personalization_service.create_personality_profile("demo_user_2")
        self.demo_users["demo_user_2"] = {
            'name': 'Bob (Technical Expert)',
            'profile': profile2,
            'description': 'Technical expert, advanced level, prefers technical communication'
        }
        
        # User 3: Creative Intermediate, Friendly
        user3_prefs = {
            'topics_of_interest': ['creative writing', 'storytelling', 'design'],
            'communication_style': 'friendly',
            'preferred_ai_model': 'claude-3-sonnet'
        }
        
        self.personalization_service.context_service = MockContextService(user3_prefs)
        
        profile3 = await self.personalization_service.create_personality_profile("demo_user_3")
        self.demo_users["demo_user_3"] = {
            'name': 'Carol (Creative Intermediate)',
            'profile': profile3,
            'description': 'Creative type, intermediate level, prefers friendly communication'
        }
        
        print(f"✅ Created {len(self.demo_users)} demo user profiles")
    
    def display_user_profiles(self):
        """Display all demo user profiles"""
        print("\n" + "=" * 70)
        print("👥 DEMO USER PERSONALITY PROFILES")
        print("=" * 70)
        
        for user_id, user_data in self.demo_users.items():
            profile = user_data['profile']
            print(f"\n🧑 {user_data['name']} ({user_id})")
            print(f"📝 {user_data['description']}")
            print(f"🎓 Learning Style: {profile.learning_style.value.replace('_', ' ').title()}")
            print(f"💬 Communication: {profile.communication_style.value.title()}")
            print(f"⚡ Expertise: {profile.expertise_level.value.title()}")
            print(f"📏 Response Length: {profile.preferred_response_length}")
            print(f"🏷️  Topics: {', '.join(profile.topics_of_interest[:3])}{'...' if len(profile.topics_of_interest) > 3 else ''}")
            print(f"🤖 Personality Traits: {', '.join([trait.value for trait in profile.personality_traits])}")
            print(f"🎯 AI Model: {profile.preferred_models[0] if profile.preferred_models else 'default'}")
            print(f"📊 Confidence: {profile.confidence_score:.1%}")
    
    async def demonstrate_personalized_prompts(self):
        """Demonstrate personalized prompt generation"""
        print("\n" + "=" * 70)
        print("🎯 PERSONALIZED PROMPT GENERATION")
        print("=" * 70)
        
        base_prompt = "You are a helpful AI assistant. Help the user learn about machine learning."
        
        for user_id, user_data in self.demo_users.items():
            print(f"\n🧑 {user_data['name']}:")
            print(f"📋 Base Prompt: {base_prompt}")
            
            personalized_prompt = await self.personalization_service.personalize_prompt(
                base_prompt=base_prompt,
                user_id=user_id,
                context_type='learning'
            )
            
            print(f"✨ Personalized Prompt:")
            print(f"   {personalized_prompt}")
            print(f"📈 Personalization Added: {len(personalized_prompt) - len(base_prompt)} characters")
    
    async def demonstrate_parameter_adaptation(self):
        """Demonstrate AI parameter adaptation"""
        print("\n" + "=" * 70)
        print("⚙️  AI PARAMETER ADAPTATION")
        print("=" * 70)
        
        base_params = {
            'temperature': 0.7,
            'max_tokens': 1000,
            'model': 'gpt-3.5-turbo'
        }
        
        print(f"📋 Base Parameters: {base_params}")
        
        for user_id, user_data in self.demo_users.items():
            print(f"\n🧑 {user_data['name']}:")
            
            adapted_params = await self.personalization_service.adapt_ai_parameters(
                user_id=user_id,
                base_params=base_params.copy()
            )
            
            print(f"✨ Adapted Parameters: {adapted_params}")
            
            # Show what changed
            changes = []
            for key, value in adapted_params.items():
                if key in base_params and base_params[key] != value:
                    changes.append(f"{key}: {base_params[key]} → {value}")
            
            if changes:
                print(f"🔄 Changes: {', '.join(changes)}")
            else:
                print("🔄 No changes applied")
    
    async def simulate_learning_interaction(self):
        """Simulate learning from user interactions"""
        print("\n" + "=" * 70)
        print("📚 LEARNING FROM USER INTERACTIONS")
        print("=" * 70)
        
        # Simulate different types of interactions
        interactions = [
            {
                'user_id': 'demo_user_1',
                'interaction': {
                    'positive_feedback': True,
                    'response_time': 1200,
                    'topic': 'web development',
                    'model_used': 'gpt-4'
                },
                'description': '👍 Positive feedback on web development help'
            },
            {
                'user_id': 'demo_user_2',
                'interaction': {
                    'negative_feedback': True,
                    'response_time': 2000,
                    'topic': 'basic concepts',
                    'model_used': 'gpt-4'
                },
                'description': '👎 Negative feedback - response too basic for expert'
            },
            {
                'user_id': 'demo_user_3',
                'interaction': {
                    'positive_feedback': True,
                    'response_time': 1500,
                    'topic': 'creative writing',
                    'model_used': 'claude-3-sonnet'
                },
                'description': '👍 Positive feedback on creative writing assistance'
            }
        ]
        
        for interaction_data in interactions:
            user_id = interaction_data['user_id']
            user_name = self.demo_users[user_id]['name']
            
            print(f"\n🧑 {user_name}: {interaction_data['description']}")
            
            # Show profile before
            profile_before = self.demo_users[user_id]['profile']
            confidence_before = profile_before.confidence_score
            topics_before = len(profile_before.topics_of_interest)
            
            # Update profile
            await self.personalization_service.update_profile_from_interaction(
                user_id=user_id,
                interaction_data=interaction_data['interaction']
            )
            
            # Get updated profile
            updated_profile = self.personalization_service.personality_cache.get(user_id)
            if updated_profile:
                confidence_after = updated_profile.confidence_score
                topics_after = len(updated_profile.topics_of_interest)
                
                print(f"📊 Confidence: {confidence_before:.1%} → {confidence_after:.1%}")
                print(f"🏷️  Topics: {topics_before} → {topics_after}")
                
                if topics_after > topics_before:
                    new_topics = set(updated_profile.topics_of_interest) - set(profile_before.topics_of_interest)
                    print(f"🆕 New Topics Learned: {', '.join(new_topics)}")
    
    async def demonstrate_conversation_flow(self):
        """Demonstrate a full personalized conversation flow"""
        print("\n" + "=" * 70)
        print("💬 PERSONALIZED CONVERSATION FLOW")
        print("=" * 70)
        
        # Simulate conversation for each user
        conversation_topics = [
            "How do I get started with programming?",
            "Explain neural networks to me",
            "Help me write a creative story"
        ]
        
        for i, (user_id, user_data) in enumerate(self.demo_users.items()):
            profile = user_data['profile']
            topic = conversation_topics[i]
            
            print(f"\n🧑 {user_data['name']} asks: \"{topic}\"")
            print(f"👤 Profile: {profile.communication_style.value} • {profile.expertise_level.value} • {profile.learning_style.value}")
            
            # Generate personalized system message
            base_system = "You are a helpful AI assistant."
            personalized_system = await self.personalization_service.personalize_prompt(
                base_prompt=base_system,
                user_id=user_id,
                context_type='general_chat'
            )
            
            # Adapt parameters
            base_params = {'temperature': 0.7, 'max_tokens': 1000}
            adapted_params = await self.personalization_service.adapt_ai_parameters(
                user_id=user_id,
                base_params=base_params
            )
            
            print(f"🎯 Personalized System Message:")
            print(f"   {personalized_system[:150]}{'...' if len(personalized_system) > 150 else ''}")
            print(f"⚙️  Adapted Parameters: temp={adapted_params['temperature']}, tokens={adapted_params['max_tokens']}")
            
            # Simulate response characteristics based on personalization
            response_style = self._generate_response_characteristics(profile)
            print(f"📝 Expected Response Style: {response_style}")
    
    def _generate_response_characteristics(self, profile):
        """Generate expected response characteristics based on profile"""
        characteristics = []
        
        if profile.expertise_level == ExpertiseLevel.BEGINNER:
            characteristics.append("step-by-step explanations")
        elif profile.expertise_level == ExpertiseLevel.ADVANCED:
            characteristics.append("technical depth")
        
        if profile.learning_style == LearningStyle.VISUAL:
            characteristics.append("visual descriptions")
        elif profile.learning_style == LearningStyle.KINESTHETIC:
            characteristics.append("hands-on examples")
        
        if profile.communication_style == CommunicationStyle.CASUAL:
            characteristics.append("friendly tone")
        elif profile.communication_style == CommunicationStyle.FORMAL:
            characteristics.append("professional tone")
        
        if PersonalityTrait.PATIENT in profile.personality_traits:
            characteristics.append("patient guidance")
        if PersonalityTrait.ENCOURAGING in profile.personality_traits:
            characteristics.append("encouraging feedback")
        
        return ", ".join(characteristics) if characteristics else "standard approach"
    
    async def show_personalization_analytics(self):
        """Show personalization analytics and insights"""
        print("\n" + "=" * 70)
        print("📈 PERSONALIZATION ANALYTICS")
        print("=" * 70)
        
        total_users = len(self.demo_users)
        
        # Analyze learning styles
        learning_styles = {}
        communication_styles = {}
        expertise_levels = {}
        
        for user_data in self.demo_users.values():
            profile = user_data['profile']
            
            learning_style = profile.learning_style.value
            learning_styles[learning_style] = learning_styles.get(learning_style, 0) + 1
            
            comm_style = profile.communication_style.value
            communication_styles[comm_style] = communication_styles.get(comm_style, 0) + 1
            
            expertise = profile.expertise_level.value
            expertise_levels[expertise] = expertise_levels.get(expertise, 0) + 1
        
        print(f"👥 Total Users Analyzed: {total_users}")
        print(f"\n🎓 Learning Style Distribution:")
        for style, count in learning_styles.items():
            percentage = (count / total_users) * 100
            print(f"   {style.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")
        
        print(f"\n💬 Communication Style Distribution:")
        for style, count in communication_styles.items():
            percentage = (count / total_users) * 100
            print(f"   {style.title()}: {count} ({percentage:.1f}%)")
        
        print(f"\n⚡ Expertise Level Distribution:")
        for level, count in expertise_levels.items():
            percentage = (count / total_users) * 100
            print(f"   {level.title()}: {count} ({percentage:.1f}%)")
        
        # Average confidence
        avg_confidence = sum(user_data['profile'].confidence_score for user_data in self.demo_users.values()) / total_users
        print(f"\n📊 Average Profile Confidence: {avg_confidence:.1%}")


class MockContextService:
    """Mock context service for demo"""
    
    def __init__(self, user_prefs=None):
        self.user_prefs = user_prefs or {}
        self.redis_client = None
    
    async def get_user_preferences(self, user_id):
        return self.user_prefs
    
    async def get_conversation_history(self, user_id, limit=10):
        # Return empty for demo
        return []


async def run_personalization_demo():
    """Run the complete personalization demonstration"""
    print("🧠 AI PERSONALIZATION SYSTEM DEMONSTRATION")
    print("Task 2.1.4: User-Specific Behavior Adaptation")
    print("=" * 70)
    
    # Initialize demo
    demo = PersonalizationDemo()
    await demo.initialize()
    
    try:
        # Create demo users with different profiles
        await demo.create_demo_users()
        
        # Display user profiles
        demo.display_user_profiles()
        
        # Demonstrate personalized prompts
        await demo.demonstrate_personalized_prompts()
        
        # Demonstrate parameter adaptation
        await demo.demonstrate_parameter_adaptation()
        
        # Simulate learning from interactions
        await demo.simulate_learning_interaction()
        
        # Demonstrate conversation flow
        await demo.demonstrate_conversation_flow()
        
        # Show analytics
        await demo.show_personalization_analytics()
        
        print("\n" + "=" * 70)
        print("✅ PERSONALIZATION DEMO COMPLETED")
        print("=" * 70)
        print("🎯 Demonstrated Features:")
        print("   • Automatic personality profiling")
        print("   • Learning style inference and adaptation")
        print("   • Communication style customization")
        print("   • Expertise level detection")
        print("   • Personalized prompt generation")
        print("   • AI parameter adaptation")
        print("   • Real-time learning from interactions")
        print("   • User preference tracking")
        print("   • Personalization analytics")
        print("   • Confidence scoring and improvement")
        print("\n🧠 Task 2.1.4: AI Personalization System fully operational!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_personalization_demo())
    exit(0 if success else 1)
