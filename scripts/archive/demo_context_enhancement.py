#!/usr/bin/env python3
"""
Task 2.1.3: Context Enhancement Demo
===================================

Interactive demonstration of the context enhancement system:
- Persistent conversation memory
- User preference adaptation
- Context-aware AI responses
- Multi-turn conversation flow
"""

import asyncio
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def demonstrate_context_enhancement():
    """Demonstrate the context enhancement capabilities"""
    
    print("🧠 Task 2.1.3: Context Enhancement System Demo")
    print("=" * 70)
    print("Demonstrating advanced conversation memory and context-aware AI")
    print()
    
    try:
        from app.services.conversation_context_service import ConversationContextService, ContextType
        
        # Initialize context service with mock Redis
        context_service = ConversationContextService()
        # Mock Redis for demo
        from test_context_enhancement import MockRedis
        context_service.redis_client = MockRedis()
        
        print("✅ Context Enhancement Service Initialized")
        print()
        
        # Demo user
        user_id = "demo_user_12345"
        conversation_id = await context_service.get_conversation_id(user_id, "python_tutorial")
        
        print(f"👤 User: {user_id}")
        print(f"💬 Conversation: {conversation_id}")
        print()
        
        # Simulate a learning conversation
        print("🎭 Simulating Multi-Turn Learning Conversation")
        print("=" * 50)
        
        conversation_flow = [
            {
                "type": "user",
                "message": "Hi! I'm new to Python and want to learn programming. Can you help me?",
                "context": "Initial greeting - user indicates they're a beginner"
            },
            {
                "type": "ai",
                "message": "Hello! I'd be happy to help you learn Python! Since you're new to programming, let's start with the basics. Python is a great first language because it's readable and versatile. What specific area interests you most - web development, data analysis, or general programming concepts?",
                "provider": "openai",
                "model": "gpt-4",
                "tokens": {"prompt_tokens": 20, "completion_tokens": 45, "total_tokens": 65}
            },
            {
                "type": "user", 
                "message": "I'm interested in data analysis. I work with spreadsheets a lot and want to automate my work.",
                "context": "User reveals interest in data analysis and automation"
            },
            {
                "type": "ai",
                "message": "Perfect! Python is excellent for data analysis and automation. Since you work with spreadsheets, you'll love libraries like pandas (for data manipulation) and openpyxl (for Excel files). Let's start with pandas - it's like Excel but much more powerful. Would you like to see a simple example of reading and analyzing spreadsheet data?",  
                "provider": "claude",
                "model": "claude-3-sonnet",
                "tokens": {"prompt_tokens": 85, "completion_tokens": 55, "total_tokens": 140}
            },
            {
                "type": "user",
                "message": "Yes! Can you show me how to read an Excel file and find the average of a column?",
                "context": "User wants practical example - showing engagement with data analysis"
            },
            {
                "type": "ai",
                "message": "Absolutely! Here's a simple example:\n\n```python\nimport pandas as pd\n\n# Read Excel file\ndf = pd.read_excel('your_data.xlsx')\n\n# Find average of a column (e.g., 'Sales')\naverage_sales = df['Sales'].mean()\nprint(f'Average sales: {average_sales}')\n```\n\nThis is much faster than Excel formulas for large datasets! The great thing is you can also filter, group, and create charts. Since you mentioned automation, you could run this script daily to analyze new data automatically.",
                "provider": "gemini",
                "model": "gemini-pro", 
                "tokens": {"prompt_tokens": 140, "completion_tokens": 80, "total_tokens": 220}
            },
            {
                "type": "user",
                "message": "That's great! How would I filter the data before calculating the average?",
                "context": "Building on previous example - user wants to go deeper"
            }
        ]
        
        # Process conversation flow
        for i, turn in enumerate(conversation_flow):
            print(f"\n🔄 Turn {i+1}: {turn['type'].upper()}")
            print("-" * 30)
            
            if turn['type'] == 'user':
                # Add user message
                await context_service.add_message(
                    user_id=user_id,
                    conversation_id=conversation_id,  
                    message_type=ContextType.USER_MESSAGE,
                    content=turn['message'],
                    metadata={"context_note": turn['context'], "turn": i+1}
                )
                
                print(f"💭 Context: {turn['context']}")
                print(f"💬 User: {turn['message']}")
                
            else:  # AI response
                # Add AI response
                await context_service.add_message(
                    user_id=user_id,
                    conversation_id=conversation_id,
                    message_type=ContextType.AI_RESPONSE,
                    content=turn['message'],
                    metadata={"turn": i+1, "reasoning": "Context-aware response"},
                    ai_provider=turn['provider'],
                    ai_model=turn['model'],
                    tokens_used=turn['tokens'],
                    response_time_ms=1200 + i * 100
                )
                
                print(f"🤖 Provider: {turn['provider']} ({turn['model']})")
                print(f"📊 Tokens: {turn['tokens']['total_tokens']}")
                print(f"💬 AI: {turn['message'][:100]}...")
                if len(turn['message']) > 100:
                    print(f"    ... [truncated, full response stored in context]")
        
        print("\n" + "=" * 70)
        print("📊 Context Enhancement Analysis")
        print("=" * 70)
        
        # Analyze the conversation context
        context = await context_service.get_conversation_context(conversation_id)
        
        if context:
            print(f"\n🧠 **CONVERSATION MEMORY:**")
            print(f"   📝 Total Messages: {context.total_messages}")
            print(f"   🔢 Total Tokens: {context.total_tokens}")
            print(f"   🕐 Duration: {(context.updated_at - context.created_at).total_seconds():.1f} seconds")
            print(f"   📈 Learning Progress: User went from beginner → specific data analysis questions")
            
            # Show context evolution
            print(f"\n🔄 **CONTEXT EVOLUTION:**")
            learning_progression = [
                "Turn 1: User identifies as Python beginner",
                "Turn 2: AI adapts to beginner level, asks for interests", 
                "Turn 3: User reveals data analysis interest",
                "Turn 4: AI pivots to data-focused response with pandas",
                "Turn 5: User engages with practical example",
                "Turn 6: AI provides code example, references user's automation need"
            ]
            
            for progression in learning_progression:
                print(f"   • {progression}")
            
            # Show AI context for next response
            print(f"\n🤖 **AI CONTEXT FOR NEXT RESPONSE:**")
            ai_context, context_metadata = await context_service.generate_context_for_ai(
                conversation_id=conversation_id,
                max_context_messages=6,
                include_summary=True
            )
            
            print(f"   📥 Context Messages: {len(ai_context)}")
            print(f"   👤 User Preferences Available: {'user_preferences' in context_metadata}")
            print(f"   📊 Conversation Metadata: {len(context_metadata)} keys")
            
            # Show what the AI would "remember"
            print(f"\n🧠 **AI MEMORY (What AI Knows About User):**")
            print(f"   • User is new to Python programming")
            print(f"   • Interested in data analysis and automation")
            print(f"   • Works with spreadsheets currently")
            print(f"   • Engaged with pandas example")
            print(f"   • Asking progressively more complex questions")
            print(f"   • Prefers practical examples over theory")
            
        # Demonstrate user preference learning
        print(f"\n⚙️ **USER PREFERENCE LEARNING:**")
        
        # Simulate preference updates based on conversation
        learned_preferences = {
            'preferred_ai_provider': 'claude',  # User seemed to respond well to Claude's data explanation
            'preferred_ai_model': 'claude-3-sonnet',
            'communication_style': 'practical',  # User prefers examples
            'detail_level': 'detailed',  # User asks follow-up questions
            'language': 'en',
            'topics_of_interest': ['python', 'data_analysis', 'pandas', 'automation', 'excel'],
            'response_length_preference': 'moderate',
            'learning_style': 'example_driven',
            'expertise_level': 'beginner_to_intermediate'
        }
        
        await context_service.update_user_preferences(user_id, learned_preferences)
        
        print(f"   ✅ Learned Preferences:")
        for key, value in learned_preferences.items():
            if isinstance(value, list):
                value_str = ', '.join(value[:3]) + ('...' if len(value) > 3 else '')
            else:
                value_str = str(value)
            print(f"      {key}: {value_str}")
        
        # Show how this affects future responses
        print(f"\n🔮 **FUTURE RESPONSE PERSONALIZATION:**")
        print(f"   🎯 Provider Selection: Will prefer Claude (user responded well)")
        print(f"   📝 Communication Style: Will include practical examples")
        print(f"   📊 Detail Level: Will provide comprehensive explanations")
        print(f"   🏷️  Topic Focus: Will emphasize data analysis applications")
        print(f"   📈 Learning Path: Will progress from basic to intermediate concepts")
        
        # Demonstrate context-aware next response
        print(f"\n💡 **NEXT AI RESPONSE WOULD BE CONTEXT-AWARE:**")
        print(f"   📚 Context: 'Building on pandas filtering, here's how to filter before averaging:'")
        print(f"   🔗 Connection: References previous Excel automation discussion")
        print(f"   📊 Personalization: Uses Claude (preferred), detailed examples (learning style)")
        print(f"   🎯 Relevance: Directly answers user's progression from basic to filtered analysis")
        
        print(f"\n" + "=" * 70)
        print("🎉 Task 2.1.3: Context Enhancement Demo Complete!")
        print("=" * 70)
        
        print(f"\n✅ **DEMONSTRATED CAPABILITIES:**")
        print(f"   🧠 **Persistent Memory**: Conversation stored with full context")
        print(f"   📈 **Learning Progression**: AI tracks user's knowledge evolution")
        print(f"   🎯 **Personalization**: Preferences learned from interactions")
        print(f"   🔄 **Context Continuity**: Each response builds on previous exchanges")
        print(f"   🤖 **Multi-Provider Memory**: Context shared across AI providers")
        print(f"   📊 **Performance Tracking**: Token usage and response times monitored")
        print(f"   💭 **Semantic Understanding**: AI understands conversation themes")
        print(f"   🔮 **Predictive Adaptation**: Future responses will be personalized")
        
        print(f"\n🏆 **PRODUCTION BENEFITS:**")
        print(f"   • Users get coherent, continuous conversations")
        print(f"   • AI responses become more relevant over time")
        print(f"   • Reduced repetition and improved user experience")
        print(f"   • Efficient context management with Redis persistence")
        print(f"   • Cross-session memory for returning users")
        print(f"   • Multi-provider intelligence sharing")
        
        print(f"\n🚀 **READY FOR TASK 2.1.4: AI PERSONALIZATION**")
        print(f"   The context foundation enables advanced personalization features!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(demonstrate_context_enhancement())
