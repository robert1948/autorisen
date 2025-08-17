#!/usr/bin/env python3
"""
Test script to send a registration notification email to contact@cape-control.com
This demonstrates the email functionality for CapeControl registrations.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append('/workspaces/localstorm/backend')

from app.email_service import email_service

async def test_registration_email():
    """Send a test registration notification"""
    
    # Sample registration data
    test_user_data = {
        'firstName': 'John',
        'lastName': 'Doe',
        'email': 'john.doe@example.com',
        'role': 'developer',
        'company': 'TechCorp Solutions',
        'phone': '+1-555-0123',
        'website': 'https://techcorp.example.com',
        'experience': 'advanced'
    }
    
    print("🚀 Sending test registration notification...")
    print(f"📧 Recipient: contact@cape-control.com")
    print(f"👤 Test User: {test_user_data['firstName']} {test_user_data['lastName']}")
    print(f"🏢 Company: {test_user_data['company']}")
    print(f"⚡ Role: {test_user_data['role']}")
    print("-" * 50)
    
    # Send the email
    success = await email_service.send_registration_notification(test_user_data)
    
    if success:
        print("✅ Registration notification sent successfully!")
        print("\n📋 Note: In development mode, this prints to console.")
        print("📧 To send actual emails, configure SMTP settings in environment variables:")
        print("   - SMTP_HOST")
        print("   - SMTP_PORT") 
        print("   - SMTP_USERNAME")
        print("   - SMTP_PASSWORD")
        print("   - FROM_EMAIL")
    else:
        print("❌ Failed to send registration notification")
    
    return success

if __name__ == "__main__":
    # Run the async function
    result = asyncio.run(test_registration_email())
    
    if result:
        print(f"\n🎉 Email notification demonstration completed!")
        print(f"📬 contact@cape-control.com would receive registration notifications")
        print(f"🔧 Ready to integrate with live SMTP service")
    else:
        print(f"\n❌ Email test failed")
