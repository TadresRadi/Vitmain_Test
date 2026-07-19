"""
Email verification service.
Generates, stores, and validates verification tokens for new user signups.
"""
import logging
import secrets
import hashlib
from typing import Optional, Tuple
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings

User = get_user_model()
logger = logging.getLogger(__name__)

EMAIL_VERIFICATION_PREFIX = "email_verify:"
EMAIL_VERIFICATION_TTL = getattr(settings, 'EMAIL_VERIFICATION_TOKEN_TTL', 86400)


class EmailVerificationService:
    """Service for managing email verification tokens."""

    @staticmethod
    def generate_token() -> str:
        """Generate a cryptographically secure verification token."""
        return secrets.token_urlsafe(32)

    @staticmethod
    def _hash_token(token: str) -> str:
        """Hash token for storage. Never store raw tokens."""
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def store_token(user: User, token: str) -> bool:
        """Store verification token for a user."""
        try:
            token_hash = EmailVerificationService._hash_token(token)
            cache_key = f"{EMAIL_VERIFICATION_PREFIX}{user.id}"
            data = {
                'token_hash': token_hash,
                'email': user.email,
                'created_at': timezone.now().isoformat(),
                'attempts': 0,
            }
            cache.set(cache_key, data, EMAIL_VERIFICATION_TTL)
            return True
        except Exception as e:
            logger.error(f"Error storing email verification token: {str(e)}")
            return False

    @staticmethod
    def validate_token(user_id: str, token: str) -> Tuple[bool, Optional[str]]:
        """
        Validate verification token.
        Returns (success, error_message).
        """
        try:
            if not token or not isinstance(token, str):
                return False, "Invalid token format"

            cache_key = f"{EMAIL_VERIFICATION_PREFIX}{user_id}"
            data = cache.get(cache_key)

            if not data:
                return False, "Verification token expired or not found"

            # Brute force protection
            attempts = data.get('attempts', 0)
            if attempts > 5:
                cache.delete(cache_key)
                return False, "Too many verification attempts"

            token_hash = EmailVerificationService._hash_token(token)
            stored_hash = data.get('token_hash')

            if not secrets.compare_digest(token_hash, stored_hash or ''):
                data['attempts'] = attempts + 1
                cache.set(cache_key, data, EMAIL_VERIFICATION_TTL)
                return False, "Invalid verification token"

            return True, None
        except Exception as e:
            logger.error(f"Error validating email verification token: {str(e)}")
            return False, "Error validating token"

    @staticmethod
    def revoke_token(user_id: str) -> None:
        """Delete verification token after successful verification."""
        cache_key = f"{EMAIL_VERIFICATION_PREFIX}{user_id}"
        cache.delete(cache_key)

    @staticmethod
    def verify_user(user_id: str, token: str) -> Tuple[bool, Optional[str]]:
        """
        Validate token and mark user as email-verified.
        Returns (success, error_message).
        """
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return False, "User not found"

        if user.is_email_verified:
            return True, "Email already verified"

        valid, err = EmailVerificationService.validate_token(user_id, token)
        if not valid:
            return False, err

        user.is_email_verified = True
        user.save(update_fields=['is_email_verified'])
        EmailVerificationService.revoke_token(user_id)

        logger.info(f"Email verified for user: {user.email}")
        return True, None

    @staticmethod
    def initiate_verification(user: User, frontend_url: str) -> bool:
        """
        Generate token, store it, and send verification email.
        Returns True if email was sent.
        """
        from core.email_service import get_email_service

        token = EmailVerificationService.generate_token()
        logger.info("Starting email verification for user: %s", user.email)

        if not EmailVerificationService.store_token(user, token):
            logger.error("Failed to store verification token for user: %s", user.email)
            return False

        logger.info("Verification token stored for user: %s", user.email)

        # Build the verification URL (for DEBUG logging and email link)
        verification_url = (
            f"{frontend_url}/verify-email"
            f"?email={user.email}"
            f"&token={token}"
        )

        # In DEBUG mode, log the full verification link so developers
        # can click it without a real email server.
        if settings.DEBUG:
            logger.info("=" * 80)
            logger.info("EMAIL VERIFICATION LINK (DEBUG MODE)")
            logger.info("User: %s", user.email)
            logger.info("Link: %s", verification_url)
            logger.info("=" * 80)

        email_service = get_email_service()
        sent = email_service.send_email_verification(
            user_email=user.email,
            verification_token=token,
            frontend_url=frontend_url,
        )

        if sent:
            logger.info("Verification email sent successfully to: %s", user.email)
        else:
            logger.warning("Verification email could not be sent to: %s (email service returned False)", user.email)

        return sent
    


# Singleton
_email_verification_service = None


def get_email_verification_service() -> EmailVerificationService:
    global _email_verification_service
    if _email_verification_service is None:
        _email_verification_service = EmailVerificationService()
    return _email_verification_service