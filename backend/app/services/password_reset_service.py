"""
Password Reset Service
Implements secure password reset functionality with SendGrid email integration
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

# Try to import SendGrid (optional dependency)
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, From, To, Subject, PlainTextContent, HtmlContent
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    logging.warning("SendGrid not available - using SMTP fallback")

from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import User
from app.auth import get_password_hash

logger = logging.getLogger(__name__)

class PasswordResetService:
    """Service for handling password reset functionality"""
    
    def __init__(self):
        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@cape-control.com')
        self.frontend_url = os.getenv('FRONTEND_URL', 'https://cape-control.com')
        self.reset_token_expiry = 3600  # 1 hour in seconds
        
        # SMTP fallback configuration
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        
    def generate_reset_token(self) -> str:
        """Generate a secure random token for password reset"""
        return secrets.token_urlsafe(32)
    
    def create_reset_token_hash(self, token: str) -> str:
        """Create a hash of the reset token for database storage"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    async def request_password_reset(self, db: Session, email: str) -> Dict[str, Any]:
        """
        Initiate password reset process
        
        Args:
            db: Database session
            email: User's email address
            
        Returns:
            Dict with success status and message
        """
        try:
            # Normalize email
            normalized_email = email.lower().strip()
            
            # Find user by email
            user = db.query(User).filter(User.email == normalized_email).first()
            
            if not user:
                # Don't reveal if email exists - security best practice
                return {
                    "success": True,
                    "message": "If an account with that email exists, you will receive password reset instructions."
                }
            
            # Generate reset token
            reset_token = self.generate_reset_token()
            token_hash = self.create_reset_token_hash(reset_token)
            
            # Store token in database (you'll need to create this table)
            expires_at = datetime.utcnow() + timedelta(seconds=self.reset_token_expiry)
            
            # For now, store in user table (you can create separate password_resets table later)
            user.password_reset_token = token_hash
            user.password_reset_expires = expires_at
            user.updated_at = datetime.utcnow()
            
            db.commit()
            
            # Send reset email
            email_sent = await self.send_reset_email(user.email, user.first_name or "User", reset_token)
            
            if email_sent:
                logger.info(f"Password reset email sent to {user.email}")
                return {
                    "success": True,
                    "message": "Password reset instructions have been sent to your email."
                }
            else:
                logger.error(f"Failed to send password reset email to {user.email}")
                return {
                    "success": False,
                    "message": "Failed to send reset email. Please try again later."
                }
                
        except Exception as e:
            logger.error(f"Password reset request failed: {e}")
            db.rollback()
            return {
                "success": False,
                "message": "An error occurred. Please try again later."
            }
    
    async def send_reset_email(self, email: str, name: str, reset_token: str) -> bool:
        """
        Send password reset email using SendGrid or SMTP fallback
        
        Args:
            email: Recipient email
            name: Recipient name
            reset_token: Reset token to include in email
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            reset_url = f"{self.frontend_url}/reset-password?token={reset_token}"
            
            # Email content
            subject = "Reset Your CapeControl Password"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Password Reset - CapeControl</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #1e3a8a; color: white; padding: 20px; text-align: center; }}
                    .content {{ background: #f9fafb; padding: 30px; }}
                    .button {{ 
                        display: inline-block; 
                        background: #2563eb; 
                        color: white; 
                        padding: 12px 24px; 
                        text-decoration: none; 
                        border-radius: 6px; 
                        margin: 20px 0;
                    }}
                    .footer {{ background: #374151; color: white; padding: 20px; text-align: center; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>CapeControl</h1>
                        <p>Password Reset Request</p>
                    </div>
                    
                    <div class="content">
                        <h2>Hello {name},</h2>
                        
                        <p>We received a request to reset your password for your CapeControl account.</p>
                        
                        <p>Click the button below to reset your password:</p>
                        
                        <a href="{reset_url}" class="button">Reset Password</a>
                        
                        <p><strong>This link will expire in 1 hour.</strong></p>
                        
                        <p>If you didn't request this password reset, please ignore this email. Your password will remain unchanged.</p>
                        
                        <p>For security reasons, never share this link with anyone.</p>
                        
                        <hr>
                        
                        <p><small>If the button doesn't work, copy and paste this link into your browser:</small></p>
                        <p><small>{reset_url}</small></p>
                    </div>
                    
                    <div class="footer">
                        <p>© 2025 CapeControl. All rights reserved.</p>
                        <p>Enterprise AI Platform | https://cape-control.com</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            Password Reset Request - CapeControl
            
            Hello {name},
            
            We received a request to reset your password for your CapeControl account.
            
            Click this link to reset your password:
            {reset_url}
            
            This link will expire in 1 hour.
            
            If you didn't request this password reset, please ignore this email.
            
            For security reasons, never share this link with anyone.
            
            © 2025 CapeControl
            https://cape-control.com
            """
            
            # Try SendGrid first, fallback to SMTP
            if SENDGRID_AVAILABLE and self.sendgrid_api_key:
                return await self._send_via_sendgrid(email, subject, text_content, html_content)
            else:
                return await self._send_via_smtp(email, subject, text_content, html_content)
                
        except Exception as e:
            logger.error(f"Failed to send reset email: {e}")
            return False
    
    async def _send_via_sendgrid(self, email: str, subject: str, text_content: str, html_content: str) -> bool:
        """Send email via SendGrid"""
        try:
            message = Mail(
                from_email=From(self.from_email, "CapeControl"),
                to_emails=To(email),
                subject=Subject(subject),
                plain_text_content=PlainTextContent(text_content),
                html_content=HtmlContent(html_content)
            )
            
            sg = SendGridAPIClient(api_key=self.sendgrid_api_key)
            response = sg.send(message)
            
            if response.status_code == 202:
                logger.info(f"SendGrid email sent successfully to {email}")
                return True
            else:
                logger.error(f"SendGrid failed with status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"SendGrid error: {e}")
            return False
    
    async def _send_via_smtp(self, email: str, subject: str, text_content: str, html_content: str) -> bool:
        """Send email via SMTP fallback"""
        try:
            if not self.smtp_username or not self.smtp_password:
                logger.error("SMTP credentials not configured")
                return False
                
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = email
            
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"SMTP email sent successfully to {email}")
            return True
            
        except Exception as e:
            logger.error(f"SMTP error: {e}")
            return False
    
    async def verify_reset_token(self, db: Session, token: str) -> Optional[User]:
        """
        Verify reset token and return user if valid
        
        Args:
            db: Database session
            token: Reset token from URL
            
        Returns:
            User object if token is valid, None otherwise
        """
        try:
            token_hash = self.create_reset_token_hash(token)
            
            # Find user with valid token
            user = db.query(User).filter(
                and_(
                    User.password_reset_token == token_hash,
                    User.password_reset_expires > datetime.utcnow()
                )
            ).first()
            
            return user
            
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None
    
    async def reset_password(self, db: Session, token: str, new_password: str) -> Dict[str, Any]:
        """
        Reset user password with valid token
        
        Args:
            db: Database session
            token: Reset token
            new_password: New password
            
        Returns:
            Dict with success status and message
        """
        try:
            # Verify token
            user = await self.verify_reset_token(db, token)
            
            if not user:
                return {
                    "success": False,
                    "message": "Invalid or expired reset token."
                }
            
            # Update password
            user.password_hash = get_password_hash(new_password)
            user.password_reset_token = None
            user.password_reset_expires = None
            user.updated_at = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"Password reset successful for user {user.email}")
            
            return {
                "success": True,
                "message": "Password reset successful. You can now log in with your new password."
            }
            
        except Exception as e:
            logger.error(f"Password reset failed: {e}")
            db.rollback()
            return {
                "success": False,
                "message": "An error occurred. Please try again."
            }

# Global service instance
password_reset_service = PasswordResetService()
