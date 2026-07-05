"""
Password management service.
Handles password changes, resets, and recovery flows.
"""
import logging
import secrets
import hashlib
from typing import Optional, Tuple, Dict, Any
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from django.urls import reverse
from core.utils import log_user_activity

User = get_user_model()
logger = logging.getLogger(__name__)

PASSWORD_RESET_TOKEN_LENGTH = 32
PASSWORD_RESET_TTL = 3600  # 1 hour
PASSWORD_RESET_PREFIX = "password_reset:"
PASSWORD_CHANGE_PREFIX = "password_change:"


class PasswordResetToken:
    """Generate and manage password reset tokens."""
    
    @staticmethod
    def generate_token() -> str:
        """
        Generate a cryptographically secure password reset token.
        
        Returns:
            32-byte hex string token
        """
        token = secrets.token_hex(PASSWORD_RESET_TOKEN_LENGTH // 2)
        logger.debug(f"Generated password reset token: {token[:8]}...")
        return token
    
    @staticmethod
    def hash_token(token: str) -> str:
        """
        Hash token for storage.
        Never store raw tokens in cache.
        
        Args:
            token: Raw token
        
        Returns:
            SHA256 hash of token
        """
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    def store_reset_token(
        email: str,
        token: str
    ) -> bool:
        """
        Store password reset token.
        
        Args:
            email: User email
            token: Reset token
        
        Returns:
            True if stored successfully
        """
        try:
            # Hash the token before storing
            token_hash = PasswordResetToken.hash_token(token)
            cache_key = f"{PASSWORD_RESET_PREFIX}{email}"
            
            data = {
                'token_hash': token_hash,
                'created_at': timezone.now().isoformat(),
                'attempts': 0,
            }
            
            cache.set(cache_key, data, PASSWORD_RESET_TTL)
            logger.debug(f"Stored password reset token for: {email}")
            return True
        
        except Exception as e:
            logger.error(f"Error storing password reset token: {str(e)}")
            return False
    
    @staticmethod
    def validate_reset_token(email: str, token: str) -> bool:
        """
        Validate password reset token.
        
        Args:
            email: User email
            token: Reset token to validate
        
        Returns:
            True if token is valid and not expired
        """
        try:
            if not token or not isinstance(token, str):
                logger.warning("Invalid reset token format")
                return False
            
            cache_key = f"{PASSWORD_RESET_PREFIX}{email}"
            data = cache.get(cache_key)
            
            if not data:
                logger.warning(f"No reset token found for: {email}")
                return False
            
            # Check attempt count (prevent brute force)
            attempts = data.get('attempts', 0)
            if attempts > 5:
                logger.warning(f"Too many reset attempts for: {email}")
                cache.delete(cache_key)
                return False
            
            # Hash provided token and compare
            token_hash = PasswordResetToken.hash_token(token)
            stored_hash = data.get('token_hash')
            
            if not secrets.compare_digest(token_hash, stored_hash or ''):
                # Increment attempts
                data['attempts'] = attempts + 1
                cache.set(cache_key, data, PASSWORD_RESET_TTL)
                logger.warning(f"Invalid reset token for: {email}")
                return False
            
            logger.debug(f"Valid reset token for: {email}")
            return True
        
        except Exception as e:
            logger.error(f"Error validating reset token: {str(e)}")
            return False
    
    @staticmethod
    def revoke_reset_token(email: str) -> bool:
        """
        Revoke/delete a password reset token.
        
        Args:
            email: User email
        
        Returns:
            True if revoked
        """
        try:
            cache_key = f"{PASSWORD_RESET_PREFIX}{email}"
            cache.delete(cache_key)
            logger.info(f"Revoked reset token for: {email}")
            return True
        
        except Exception as e:
            logger.error(f"Error revoking reset token: {str(e)}")
            return False


class PasswordService:
    """Service for password operations."""
    
    @staticmethod
    def change_password(
        user: User,
        old_password: str,
        new_password: str
    ) -> Tuple[bool, str]:
        """
        Change user password.
        Requires verification of old password.
        
        Args:
            user: User instance
            old_password: Current password
            new_password: New password
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Verify old password
            if not user.check_password(old_password):
                logger.warning(f"Invalid old password for user: {user.email}")
                return False, "Current password is incorrect"
            
            # Verify new password is different
            if user.check_password(new_password):
                return False, "New password must be different from current password"
            
            # Update password
            user.set_password(new_password)
            user.save()
            
            log_user_activity(user, 'password_changed', {
                'timestamp': timezone.now().isoformat()
            })
            
            logger.info(f"Password changed for user: {user.email}")
            return True, "Password changed successfully"
        
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            return False, "Error changing password"
    
    @staticmethod
    def initiate_password_reset(email: str) -> Tuple[bool, str, Optional[str]]:
        """
        Initiate password reset flow.
        Generate reset token and send email.
        
        Args:
            email: User email
        
        Returns:
            Tuple of (success, message, reset_token)
        """
        try:
            # Find user by email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # Don't reveal if user exists
                logger.info(f"Password reset requested for non-existent email: {email}")
                return True, "If an account exists with this email, a reset link has been sent", None
            
            # Check if user has password (OAuth users might not)
            if not user.password:
                return False, "Password reset not available for this account type"
            
            # Generate reset token
            token = PasswordResetToken.generate_token()
            
            # Store token
            if not PasswordResetToken.store_reset_token(email, token):
                return False, "Error initiating password reset"
            
            log_user_activity(user, 'password_reset_initiated', {
                'email': email,
                'timestamp': timezone.now().isoformat()
            })
            
            logger.info(f"Password reset initiated for user: {email}")
            
            # Return success with token (will be sent via email separately)
            return True, "Password reset link sent to your email", token
        
        except Exception as e:
            logger.error(f"Error initiating password reset: {str(e)}")
            return False, "Error processing password reset"
    
    @staticmethod
    def reset_password(
        email: str,
        token: str,
        new_password: str
    ) -> Tuple[bool, str]:
        """
        Reset password using valid token.
        
        Args:
            email: User email
            token: Reset token
            new_password: New password
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Validate token
            if not PasswordResetToken.validate_reset_token(email, token):
                return False, "Invalid or expired reset token"
            
            # Get user
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return False, "User not found"
            
            # Update password
            user.set_password(new_password)
            user.save()
            
            # Revoke token
            PasswordResetToken.revoke_reset_token(email)
            
            log_user_activity(user, 'password_reset_completed', {
                'email': email,
                'timestamp': timezone.now().isoformat()
            })
            
            logger.info(f"Password reset completed for user: {email}")
            return True, "Password reset successfully"
        
        except Exception as e:
            logger.error(f"Error resetting password: {str(e)}")
            return False, "Error resetting password"
    
    @staticmethod
    def is_password_secure(password: str) -> Tuple[bool, Optional[str]]:
        """
        Check if password meets security requirements.
        
        Args:
            password: Password to check
        
        Returns:
            Tuple of (is_secure, error_message)
        """
        from core.validators import InputValidator, ValidatorError
        
        try:
            InputValidator.validate_password(password)
            return True, None
        except ValidatorError as e:
            return False, str(e)


# Singleton instance
_password_service = None


def get_password_service() -> PasswordService:
    """Get password service singleton."""
    global _password_service
    if _password_service is None:
        _password_service = PasswordService()
    return _password_service