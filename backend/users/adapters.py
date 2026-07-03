import logging
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from core.utils import log_user_activity

User = get_user_model()
logger = logging.getLogger(__name__)


class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        if commit:
            user.save()
            log_user_activity(user, 'register', {
                'auth_provider': user.auth_provider,
                'user_type': user.user_type,
            })
        return user


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Called before social login is completed.
        Handle account linking for existing users with the same email.
        """
        # If the social account already exists, do nothing
        if sociallogin.is_existing:
            return

        # Get the email from the social account
        email = sociallogin.account.extra_data.get('email')
        if not email:
            return

        # Try to find an existing user with this email
        try:
            user = User.objects.get(email=email)
            
            # If user exists and has local auth, link the social account
            if user.auth_provider == 'local':
                # Link the social account to the existing user
                sociallogin.connect(request, user)
                logger.info(f"Linked Google account to existing local user: {email}")
                
                # Update user with Google data if needed
                extra_data = sociallogin.account.extra_data
                if extra_data.get('picture') and not user.profile_picture:
                    user.profile_picture = extra_data.get('picture')
                if extra_data.get('name') and not user.full_name:
                    user.full_name = extra_data.get('name')
                user.save()
                
                log_user_activity(user, 'google_account_linked', {
                    'provider': sociallogin.account.provider,
                })
        except User.DoesNotExist:
            # User doesn't exist, will be created by allauth
            pass

    def save_user(self, request, sociallogin, form=None):
        """
        Save the user from social login with custom logic.
        """
        user = super().save_user(request, sociallogin, form)
        
        # Set auth provider to google
        user.auth_provider = 'google'
        
        # Update user with Google data
        extra_data = sociallogin.account.extra_data
        if extra_data.get('picture'):
            user.profile_picture = extra_data.get('picture')
        if extra_data.get('name'):
            user.full_name = extra_data.get('name')
        
        user.save()
        
        log_user_activity(user, 'google_login', {
            'provider': sociallogin.account.provider,
            'email': user.email,
        })
        
        return user
