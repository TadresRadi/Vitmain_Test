"""
Google OAuth authentication service.
Handles token verification, user lookup, creation, and linking.
"""
import logging
import requests
from typing import Optional, Tuple, Dict, Any
from urllib.parse import urlparse
from django.contrib.auth import get_user_model
from django.conf import settings
from allauth.socialaccount.models import SocialAccount
from core.services import ServiceException
from core.utils import log_user_activity
from .user_service import get_user_service


User = get_user_model()
logger = logging.getLogger(__name__)


class GoogleAuthService:
    """
    Service for Google OAuth operations.
    Handles token verification, user authentication, and account linking.
    """
    
    GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"
    TIMEOUT = 10
    MAX_RETRIES = 2
    ALLOWED_PICTURE_DOMAINS = ('google', 'googleapis', 'gstatic', 'lh3', 'lh4', 'lh5', 'lh6')
    
    def __init__(self):
        self.user_service = get_user_service()
    
    def verify_id_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify Google ID token with comprehensive validation.
        
        Args:
            id_token: The ID token from Google
        
        Returns:
            Token payload dict if valid, None otherwise
        
        Raises:
            ServiceException: For configuration errors
        """
        # Validate input
        if not id_token or not isinstance(id_token, str):
            logger.warning("Invalid id_token format")
            return None
        
        # Validate configuration
        if not settings.GOOGLE_CLIENT_ID:
            logger.error("GOOGLE_CLIENT_ID not configured")
            raise ServiceException("Google OAuth not configured on server")
        
        if not settings.GOOGLE_CLIENT_SECRET:
            logger.error("GOOGLE_CLIENT_SECRET not configured")
            raise ServiceException("Google OAuth not configured on server")
        
        # Verify token with Google
        try:
            response = requests.get(
                self.GOOGLE_TOKENINFO_URL,
                params={"id_token": id_token},
                timeout=self.TIMEOUT,
            )
        except requests.Timeout:
            logger.error("Google token verification timeout after %s seconds", self.TIMEOUT)
            raise ServiceException("Authentication service timeout")
        except requests.RequestException as e:
            logger.error(f"Google token request failed: {str(e)}")
            raise ServiceException("Authentication service unavailable")
        
        # Check response status
        if response.status_code != 200:
            logger.warning(f"Google token verification failed: {response.status_code}")
            return None
        
        payload = response.json()
        
        # Validate token payload
        validation_errors = self._validate_token_payload(payload)
        if validation_errors:
            for error in validation_errors:
                logger.warning(f"Token validation failed: {error}")
            return None
        
        return payload
    
    def _validate_token_payload(self, payload: Dict[str, Any]) -> list[str]:
        """
        Validate token payload for required fields.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Validate audience
        if payload.get("aud") != settings.GOOGLE_CLIENT_ID:
            errors.append(
                f"Token audience {payload.get('aud')} doesn't match "
                f"configured {settings.GOOGLE_CLIENT_ID}"
            )
        
        # Validate email verification
        if payload.get("email_verified") not in (True, "true", "True"):
            errors.append("Email not verified by Google")
        
        # Validate required fields
        required_fields = ["email", "sub"]
        for field in required_fields:
            if not payload.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Validate email format
        email = payload.get("email", "")
        if "@" not in email or len(email) > 254:
            errors.append(f"Invalid email format: {email}")
        
        return errors
    
    def validate_picture_url(self, url: Optional[str]) -> Optional[str]:
        """
        Validate and sanitize profile picture URL.
        
        Args:
            url: Picture URL from Google
        
        Returns:
            Validated URL or None
        """
        if not url:
            return None
        
        try:
            parsed = urlparse(url)
            
            # Only allow HTTPS
            if parsed.scheme != 'https':
                logger.warning(f"Profile picture URL not HTTPS: {parsed.scheme}")
                return None
            
            # Whitelist domains
            domain_allowed = any(
                domain in parsed.netloc 
                for domain in self.ALLOWED_PICTURE_DOMAINS
            )
            if not domain_allowed:
                logger.warning(f"Profile picture from untrusted domain: {parsed.netloc}")
                return None
            
            # Check URL length
            if len(url) > 500:
                logger.warning("Profile picture URL too long")
                return None
            
            return url
        except Exception as e:
            logger.warning(f"Failed to parse picture URL: {str(e)}")
            return None
    
    def sanitize_full_name(self, name: Optional[str]) -> Optional[str]:
        """
        Sanitize full name to prevent XSS and injection attacks.
        
        Args:
            name: Full name from Google
        
        Returns:
            Sanitized name or None
        """
        if not name:
            return None
        
        try:
            # Convert to string and strip whitespace
            name = str(name).strip()
            
            # Limit length
            if len(name) > 255:
                name = name[:255]
            
            # Only allow safe characters
            import re
            if not re.match(r"^[\w\s\-'.]+$", name, re.UNICODE):
                logger.warning(f"Full name contains suspicious characters: {name[:50]}")
                return None
            
            return name
        except Exception as e:
            logger.warning(f"Error sanitizing full name: {str(e)}")
            return None
    
    def authenticate_user(
        self,
        email: str,
        user_info: Dict[str, Any]
    ) -> Tuple[User, bool]:
        """
        Authenticate or create user from Google OAuth data.
        
        Handles three cases:
        1. User exists with Google auth → update if needed, return user
        2. User exists with local auth → link Google account
        3. User doesn't exist → create new user with Google auth
        
        Args:
            email: User email from Google
            user_info: User info dict from Google token verification
        
        Returns:
            Tuple of (User instance, created_flag)
        
        Raises:
            ServiceException: If operation fails
        """
        try:
            # Try to get existing user
            existing_user = self.user_service.get_user_by_email(email)
            
            if existing_user:
                # Update existing user
                self._update_user_from_google(existing_user, user_info)
                
                # Link social account if not already linked
                if existing_user.auth_provider == 'local':
                    self._link_social_account(existing_user, user_info)
                
                log_user_activity(existing_user, 'google_login', {'email': email})
                return existing_user, False
            
            # Create new user
            new_user = self._create_google_user(email, user_info)
            log_user_activity(new_user, 'google_register', {'email': email})
            return new_user, True
            
        except ServiceException:
            raise
        except Exception as e:
            logger.error(f"Error authenticating user {email}: {str(e)}", exc_info=True)
            raise ServiceException("Failed to authenticate user")
    
    def _update_user_from_google(self, user: User, user_info: Dict[str, Any]) -> None:
        """Update existing user with Google data."""
        updated = False
        
        # Update profile picture
        picture = self.validate_picture_url(user_info.get('picture'))
        if picture and not user.profile_picture:
            user.profile_picture = picture
            updated = True
        
        # Update full name
        full_name = self.sanitize_full_name(user_info.get('name'))
        if full_name and not user.full_name:
            user.full_name = full_name
            updated = True
        
        if updated:
            user.save()
            logger.info(f"Updated user {user.email} with Google data")
    
    def _link_social_account(self, user: User, user_info: Dict[str, Any]) -> None:
        """Link Google social account to existing user."""
        try:
            social_account, created = SocialAccount.objects.get_or_create(
                user=user,
                provider='google',
                defaults={
                    'uid': user_info.get('sub'),
                    'extra_data': user_info,
                }
            )
            
            if not created:
                # Update extra data
                social_account.extra_data = user_info
                social_account.save()
            
            log_user_activity(user, 'social_account_linked', {
                'provider': 'google',
                'uid': user_info.get('sub'),
            })
            logger.info(f"Linked Google account to user: {user.email}")
        except Exception as e:
            logger.error(f"Error linking social account: {str(e)}")
            raise ServiceException("Failed to link social account")
    
    def _create_google_user(self, email: str, user_info: Dict[str, Any]) -> User:
        """Create new user from Google OAuth data."""
        try:
            # Sanitize data
            full_name = self.sanitize_full_name(user_info.get('name'))
            picture = self.validate_picture_url(user_info.get('picture'))
            
            # Create user
            user = User.objects.create_user(
                email=email,
                password=None,  # No password for OAuth users
                full_name=full_name or '',
                auth_provider='google',
                profile_picture=picture or '',
                onboarding_completed=False,
                role='user',
                user_type='explorer'
            )
            
            # Create social account
            SocialAccount.objects.create(
                user=user,
                provider='google',
                uid=user_info.get('sub'),
                extra_data=user_info,
            )
            
            logger.info(f"Created new Google user: {email}")
            return user
        except Exception as e:
            logger.error(f"Error creating Google user {email}: {str(e)}")
            raise ServiceException("Failed to create user")


# Singleton instance
_google_auth_service = None


def get_google_auth_service() -> GoogleAuthService:
    """Get or create Google auth service singleton."""
    global _google_auth_service
    if _google_auth_service is None:
        _google_auth_service = GoogleAuthService()
    return _google_auth_service

def get_or_create_google_user(email: str, user_info: Dict[str, Any]) -> Tuple[User, bool]:
    """
    Backward-compatible helper for Google OAuth views.
    """
    service = get_google_auth_service()
    return service.authenticate_user(email, user_info)