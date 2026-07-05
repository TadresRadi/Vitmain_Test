"""
Django-allauth custom adapters for Google OAuth.
"""
import logging
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from users.services import GoogleAuthService
from core.utils import log_user_activity

User = get_user_model()
logger = logging.getLogger(__name__)


class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom account adapter for local authentication."""
    
    def save_user(self, request, user, form, commit=True):
        """Save user after signup."""
        user = super().save_user(request, user, form, commit=False)
        if commit:
            user.save()
            log_user_activity(user, 'user_registered_local', {
                'email': user.email,
            })
        return user


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom social account adapter for Google OAuth."""
    
    def pre_social_login(self, request, sociallogin):
        """
        Called before social login is completed.
        Handle account linking for existing users with the same email.
        """
        if sociallogin.is_existing:
            return
        
        email = sociallogin.account.extra_data.get('email')
        if not email:
            return
        
        try:
            user = User.objects.get(email=email)
            
            if user.auth_provider == 'local':
                # Link social account
                sociallogin.connect(request, user)
                logger.info(f"Pre-linked Google account to local user: {email}")
                
                # Update user profile
                extra_data = sociallogin.account.extra_data
                if extra_data.get('picture') and not user.profile_picture:
                    user.profile_picture = extra_data.get('picture')
                if extra_data.get('name') and not user.full_name:
                    user.full_name = extra_data.get('name')
                user.save()
        except User.DoesNotExist:
            pass
        except Exception as e:
            logger.error(f"Error in pre_social_login: {str(e)}")
    
    def save_user(self, request, sociallogin, form=None):
        """Save user from social login."""
        user = super().save_user(request, sociallogin, form)
        
        try:
            # Use service to update user
            google_service = GoogleAuthService()
            extra_data = sociallogin.account.extra_data
            
            user.auth_provider = 'google'
            
            # Sanitize and update data
            full_name = google_service.sanitize_full_name(extra_data.get('name'))
            picture = google_service.validate_picture_url(extra_data.get('picture'))
            
            if full_name:
                user.full_name = full_name
            if picture:
                user.profile_picture = picture
            
            user.save()
            
            log_user_activity(user, 'user_registered_google', {
                'email': user.email,
                'provider': sociallogin.account.provider,
            })
        except Exception as e:
            logger.error(f"Error saving social user: {str(e)}")
        
        return user