#!/usr/bin/env python3
"""
Quick Email Test for CapeControl
================================

Test the Gmail SMTP configuration with the new app password.
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

from app.email_service import EmailService

async def test_email():
    """Test sending an email with the current configuration"""
    
    print("🚀 Testing CapeControl Email Configuration")
    print("=" * 50)
    
    # Initialize email service
    email_service = EmailService()
    
    print(f"📧 SMTP Host: {email_service.smtp_host}")
    print(f"📧 SMTP Port: {email_service.smtp_port}")
    print(f"📧 SMTP Username: {email_service.smtp_username}")
    print(f"📧 From Email: {email_service.from_email}")
    print(f"📧 Admin Email: {email_service.admin_email}")
    print()
    
    # Check if credentials are configured
    if not email_service.smtp_username or not email_service.smtp_password:
        print("❌ Email credentials not configured properly")
        print("💡 Make sure SMTP_USERNAME and SMTP_PASSWORD are set in .env")
        return False
    
    # Test email content
    subject = "🎉 CapeControl Email Test - Configuration Working!"
    
    html_content = """
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
          <h2 style="color: #2563eb;">🎉 CapeControl Email Test</h2>
          
          <p>Congratulations! Your email configuration is working perfectly.</p>
          
          <div style="background: #f0f9ff; border-left: 4px solid #2563eb; padding: 15px; margin: 20px 0;">
            <h3 style="margin-top: 0;">✅ Configuration Verified:</h3>
            <ul>
              <li>Gmail SMTP connection established</li>
              <li>App password authentication successful</li>
              <li>Email delivery working</li>
            </ul>
          </div>
          
          <h3>🚀 Ready for Production:</h3>
          <ul>
            <li>User registration notifications</li>
            <li>Password reset emails</li>
            <li>Welcome emails for Phase 2 onboarding</li>
            <li>Developer earnings notifications</li>
          </ul>
          
          <div style="margin-top: 30px; padding: 15px; background: #ecfdf5; border-radius: 5px;">
            <p style="margin: 0;"><strong>Next Step:</strong> Deploy these email settings to Heroku!</p>
          </div>
          
          <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
          <p style="color: #6b7280; font-size: 14px;">
            This email was sent by the CapeControl backend system.<br>
            Timestamp: $(date)<br>
            Environment: Development
          </p>
        </div>
      </body>
    </html>
    """
    
    text_content = """
    CapeControl Email Test - Configuration Working!
    
    Congratulations! Your email configuration is working perfectly.
    
    Configuration Verified:
    ✅ Gmail SMTP connection established
    ✅ App password authentication successful  
    ✅ Email delivery working
    
    Ready for Production:
    - User registration notifications
    - Password reset emails
    - Welcome emails for Phase 2 onboarding
    - Developer earnings notifications
    
    Next Step: Deploy these email settings to Heroku!
    
    ---
    This email was sent by the CapeControl backend system.
    Environment: Development
    """
    
    try:
        print("📤 Sending test email...")
        success = await email_service.send_email(
            to_email=email_service.admin_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
        
        if success:
            print("✅ Email sent successfully!")
            print(f"📬 Check your inbox at {email_service.admin_email}")
            return True
        else:
            print("❌ Failed to send email")
            return False
            
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_email())
    print("=" * 50)
    if result:
        print("🎉 Email configuration test PASSED!")
        print("📧 Ready to deploy to Heroku!")
    else:
        print("💥 Email configuration test FAILED!")
        print("🔧 Check your settings and try again.")
