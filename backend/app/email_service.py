import os
from email.message import EmailMessage

import aiosmtplib
from jinja2 import Template


class EmailService:
    def __init__(self):
        # Email configuration from environment variables
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@capecontrol.com")
        self.admin_email = os.getenv("ADMIN_EMAIL", "contact@cape-control.com")
        
    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str, 
        text_content: str | None = None
    ):
        """Send an email using SMTP"""
        try:
            message = EmailMessage()
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = subject
            
            if text_content:
                message.set_content(text_content)
            
            if html_content:
                message.add_alternative(html_content, subtype="html")
            
            # For development/testing, print email instead of sending
            if not self.smtp_username or not self.smtp_password:
                print("\n📧 EMAIL NOTIFICATION (Development Mode)")
                print(f"To: {to_email}")
                print(f"Subject: {subject}")
                print(f"Content:\n{html_content or text_content}")
                print("="*50)
                return True
            
            # Send via SMTP with timeout protection
            import asyncio
            await asyncio.wait_for(
                aiosmtplib.send(
                    message,
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    start_tls=True,
                    username=self.smtp_username,
                    password=self.smtp_password,
                ),
                timeout=10.0  # 10 second timeout for SMTP operations
            )
            return True
            
        except TimeoutError:
            print(f"⏰ Email sending timeout for {to_email}")
            return False
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    async def send_registration_notification(self, user_data: dict):
        """Send registration notification to admin"""
        
        # HTML template for the email
        html_template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>New Registration - CapeControl</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #4F46E5; color: white; padding: 20px; text-align: center; }
                .content { background: #f9f9f9; padding: 20px; }
                .detail { margin: 10px 0; }
                .label { font-weight: bold; color: #4F46E5; }
                .value { margin-left: 10px; }
                .footer { background: #e5e5e5; padding: 15px; text-align: center; font-size: 0.9em; }
                .role-badge { 
                    display: inline-block; 
                    padding: 4px 12px; 
                    border-radius: 20px; 
                    font-size: 0.9em; 
                    font-weight: bold;
                }
                .user-role { background: #10B981; color: white; }
                .developer-role { background: #F59E0B; color: white; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 New Registration on CapeControl</h1>
                </div>
                
                <div class="content">
                    <p>A new user has registered on the CapeControl platform!</p>
                    
                    <div class="detail">
                        <span class="label">Name:</span>
                        <span class="value">{{ user_data.firstName }} {{ user_data.lastName }}</span>
                    </div>
                    
                    <div class="detail">
                        <span class="label">Email:</span>
                        <span class="value">{{ user_data.email }}</span>
                    </div>
                    
                    <div class="detail">
                        <span class="label">Role:</span>
                        <span class="value">
                            <span class="role-badge {{ 'user-role' if user_data.role == 'user' else 'developer-role' }}">
                                {{ user_data.role.title() }}
                            </span>
                        </span>
                    </div>
                    
                    {% if user_data.company %}
                    <div class="detail">
                        <span class="label">Company:</span>
                        <span class="value">{{ user_data.company }}</span>
                    </div>
                    {% endif %}
                    
                    {% if user_data.phone %}
                    <div class="detail">
                        <span class="label">Phone:</span>
                        <span class="value">{{ user_data.phone }}</span>
                    </div>
                    {% endif %}
                    
                    {% if user_data.website %}
                    <div class="detail">
                        <span class="label">Website:</span>
                        <span class="value">{{ user_data.website }}</span>
                    </div>
                    {% endif %}
                    
                    {% if user_data.experience %}
                    <div class="detail">
                        <span class="label">Experience:</span>
                        <span class="value">{{ user_data.experience.title() }}</span>
                    </div>
                    {% endif %}
                    
                    <div class="detail">
                        <span class="label">Registration Time:</span>
                        <span class="value">{{ timestamp }}</span>
                    </div>
                </div>
                
                <div class="footer">
                    <p>This is an automated notification from CapeControl.</p>
                    <p>Visit your admin dashboard to manage users and view detailed analytics.</p>
                </div>
            </div>
        </body>
        </html>
        """)
        
        from datetime import datetime
        
        # Render the email content
        html_content = html_template.render(
            user_data=user_data,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        )
        
        # Text version for email clients that don't support HTML
        text_content = f"""
New Registration on CapeControl

Name: {user_data.get('firstName', '')} {user_data.get('lastName', '')}
Email: {user_data.get('email', '')}
Role: {user_data.get('role', '').title()}
Company: {user_data.get('company', 'N/A')}
Phone: {user_data.get('phone', 'N/A')}
Website: {user_data.get('website', 'N/A')}
Experience: {user_data.get('experience', 'N/A').title()}
Registration Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}

This is an automated notification from CapeControl.
        """
        
        # Send email to admin
        success = await self.send_email(
            to_email=self.admin_email,
            subject=f"🎉 New {user_data.get('role', 'User').title()} Registration - {user_data.get('firstName', '')} {user_data.get('lastName', '')}",
            html_content=html_content,
            text_content=text_content
        )
        
        return success

# Create a global instance
email_service = EmailService()
