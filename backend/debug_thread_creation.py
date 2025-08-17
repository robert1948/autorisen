"""
Quick debug test for thread creation issue
"""

import asyncio
import sys
sys.path.insert(0, '/home/robert/Documents/localstorm250722/backend')

from app.services.conversation_manager import (
    EnhancedConversation,
    MessageRole,
    create_conversation_manager
)

async def debug_thread_creation():
    """Debug the thread creation issue"""
    print("🔍 Debugging thread creation...")
    
    try:
        # Create conversation manager
        config = {"auto_threading_enabled": True}
        manager = create_conversation_manager(config)
        
        # Create conversation
        conversation_data = {
            "title": "Debug Test Conversation",
            "description": "Testing thread creation",
            "conversation_type": "technical",
            "auto_threading": True
        }
        
        conversation = await manager.create_conversation("debug_user", conversation_data)
        print(f"✅ Created conversation: {conversation.conversation_id}")
        
        # Add messages
        msg1 = await manager.add_message(conversation.conversation_id, MessageRole.USER, "First message")
        msg2 = await manager.add_message(conversation.conversation_id, MessageRole.ASSISTANT, "Second message")
        msg3 = await manager.add_message(conversation.conversation_id, MessageRole.USER, "Third message")
        msg4 = await manager.add_message(conversation.conversation_id, MessageRole.ASSISTANT, "Fourth message")
        
        print(f"✅ Added 4 messages")
        
        # Get updated conversation
        updated_conversation = await manager.get_conversation(conversation.conversation_id)
        print(f"✅ Retrieved updated conversation with {len(updated_conversation.messages)} messages")
        
        # Test thread creation
        message_ids = [msg1.message_id, msg2.message_id, msg3.message_id, msg4.message_id]
        print(f"📝 Message IDs: {message_ids}")
        
        # Create thread
        thread = await updated_conversation.create_thread(
            "Debug Thread",
            message_ids,
            "debug"
        )
        
        print(f"✅ Created thread: {thread.thread_id}")
        print(f"📊 Thread details:")
        print(f"   - Title: {thread.title}")
        print(f"   - Type: {thread.thread_type}")
        print(f"   - Message count: {thread.message_count}")
        print(f"   - Participants: {thread.participants}")
        
        # Verify messages are threaded
        threaded_messages = [msg for msg in updated_conversation.messages if msg.thread_id == thread.thread_id]
        print(f"📨 Threaded messages: {len(threaded_messages)}")
        
        # Check conversation thread count
        print(f"🧵 Total threads in conversation: {len(updated_conversation.threads)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(debug_thread_creation())
    if result:
        print("✅ Debug completed successfully")
    else:
        print("❌ Debug failed")
