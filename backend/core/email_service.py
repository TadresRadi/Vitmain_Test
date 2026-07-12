"""
Email service for sending notifications.
Handles password resets, email verification, etc.
"""
import logging
from typing import List, Optional, Dict, Any
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.cache import cache

logger = logging.getLogger(__name__)

EMAIL_SEND_COOLDOWN = 300  # 5 minutes between emails to same address


class EmailService:
    """Service for sending emails."""
    
    @staticmethod
    def send_password_reset_email(
        user_email: str,
        reset_token: str,
        frontend_url: str
    ) -> bool:
        """
        Send password reset email.
        
        Args:
            user_email: Recipient email
            reset_token: Password reset token
            frontend_url: Frontend base URL
        
        Returns:
            True if sent successfully
        """
        try:
            # Check cooldown to prevent spam
            if not EmailService._check_email_cooldown(user_email, 'password_reset'):
                logger.warning("Email cooldown active — skipping send")
                return False
            
            # Build reset link
            reset_link = f"{frontend_url}/reset-password?token={reset_token}&email={user_email}"
            
            # Prepare email context
            context = {
                'user_email': user_email,
                'reset_link': reset_link,
                'token': reset_token,
                'expiry_minutes': 60,
                'app_name': 'Vitmain',
            }
            
            # Render email template
            html_message = render_to_string(
                'emails/password_reset.html',
                context
            )
            plain_message = render_to_string(
                'emails/password_reset.txt',
                context
            )
            
            # Send email
            subject = 'Password Reset Request - Vitmain'
            success = EmailService._send_email(
                subject=subject,
                plain_message=plain_message,
                html_message=html_message,
                recipient_list=[user_email],
            )
            
            if success:
                # Log without PII — email addresses should not appear in logs
                logger.info("Password reset email sent successfully")
            
            return success
        
        except Exception as e:
            logger.error(f"Error sending password reset email: {str(e)}")
            return False
    
    @staticmethod
    def send_email_verification(
        user_email: str,
        verification_token: str,
        frontend_url: str
    ) -> bool:
        """
        Send email verification link.
        
        Args:
            user_email: Recipient email
            verification_token: Verification token
            frontend_url: Frontend base URL
        
        Returns:
            True if sent successfully
        """
        try:
            # Check cooldown
            if not EmailService._check_email_cooldown(user_email, 'email_verification'):
                logger.warning(f"Email cooldown active for: {user_email}")
                return False
            
            # Build verification link
            verify_link = (
                f"{frontend_url}/verify-email?token={verification_token}&email={user_email}"
            )
            
            # Prepare context
            context = {
                'user_email': user_email,
                'verification_link': verify_link,
                'token': verification_token,
                'expiry_hours': 24,
                'app_name': 'Vitmain',
            }
            
            # Render templates
            html_message = render_to_string(
                'emails/email_verification.html',
                context
            )
            plain_message = render_to_string(
                'emails/email_verification.txt',
                context
            )
            
            # Send email
            subject = 'Verify Your Email - Vitmain'
            success = EmailService._send_email(
                subject=subject,
                plain_message=plain_message,
                html_message=html_message,
                recipient_list=[user_email],
            )
            
            if success:
                logger.info(f"Email verification sent to: {user_email}")
            
            return success
        
        except Exception as e:
            logger.error(f"Error sending email verification: {str(e)}")
            return False
    
    @staticmethod
    def send_password_change_confirmation(user_email: str) -> bool:
        """
        Send password change confirmation email.
        
        Args:
            user_email: Recipient email
        
        Returns:
            True if sent successfully
        """
        try:
            context = {
                'user_email': user_email,
                'timestamp': __import__('django.utils.timezone', fromlist=['now']).now(),
                'app_name': 'Vitmain',
            }
            
            html_message = render_to_string(
                'emails/password_change_confirmation.html',
                context
            )
            plain_message = render_to_string(
                'emails/password_change_confirmation.txt',
                context
            )
            
            subject = 'Password Changed - Vitmain'
            return EmailService._send_email(
                subject=subject,
                plain_message=plain_message,
                html_message=html_message,
                recipient_list=[user_email],
            )
        
        except Exception as e:
            logger.error(f"Error sending password change confirmation: {str(e)}")
            return False
    
    @staticmethod
    def _send_email(
        subject: str,
        plain_message: str,
        html_message: str,
        recipient_list: List[str],
        from_email: Optional[str] = None
    ) -> bool:
        """
        Send email with HTML and plain text versions.
        
        Args:
            subject: Email subject
            plain_message: Plain text body
            html_message: HTML body
            recipient_list: List of recipient emails
            from_email: Sender email (uses default if None)
        
        Returns:
            True if sent successfully
        """
        try:
            from_email = from_email or settings.DEFAULT_FROM_EMAIL
            
            # Create email with both plain text and HTML
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=from_email,
                to=recipient_list,
            )
            
            # Attach HTML version
            email.attach_alternative(html_message, 'text/html')
            
            # Send
            email.send(fail_silently=False)
            logger.debug(f"Email sent to: {recipient_list}")
            return True
        
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    @staticmethod
    def _check_email_cooldown(
        email: str,
        email_type: str
    ) -> bool:
        """
        Check if email can be sent (prevents spam).
        
        Args:
            email: Email address
            email_type: Type of email (for separate cooldowns)
        
        Returns:
            True if can send, False if on cooldown
        """
        cache_key = f"email_cooldown:{email_type}:{email}"
        
        if cache.get(cache_key):
            return False
        
        # Set cooldown
        cache.set(cache_key, True, EMAIL_SEND_COOLDOWN)
        return True


# Singleton instance
_email_service = None


def get_email_service() -> EmailService:
    """Get email service singleton."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service