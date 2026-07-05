import email
import logging
import requests
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from allauth.socialaccount.models import SocialAccount
from core.utils import log_user_activity
from users.services.google_auth_service import get_or_create_google_user


User = get_user_model()
logger = logging.getLogger(__name__)


GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"


from typing import Optional, Dict, Any

def verify_google_id_token(id_token: str) -> Optional[Dict[str, Any]]:
    """
    Verify Google ID token.
    
    Args:
        id_token: The ID token string from Google
    
    Returns:
        Dict with token payload if valid, None otherwise
    
    Raises:
        None (logs errors instead)
    """
    user, created = get_or_create_google_user(email, user_info)


class GoogleOAuthCallbackView(APIView):
    """
    Handle Google OAuth callback and return JWT tokens.
    This view is called after successful Google OAuth authentication.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            # The frontend sends Google's ID token in the legacy access_token field.
            id_token = request.data.get('id_token') or request.data.get('access_token')
            if not id_token:
                return Response(
                    {'error': 'Google credential token is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user_info = verify_google_id_token(id_token)
            if not user_info:
                return Response(
                    {'error': 'Invalid Google credential'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            email = user_info.get('email')
            if not email:
                return Response(
                    {'error': 'Email is required from Google'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get or create the user
            try:
                user = User.objects.get(email=email)
                
                # Update user with Google data if needed
                if user.auth_provider == 'google':
                    if user_info.get('picture') and not user.profile_picture:
                        user.profile_picture = user_info.get('picture')
                    if user_info.get('name') and not user.full_name:
                        user.full_name = user_info.get('name')
                    user.save()
                
                # Link Google account if user exists with local auth
                elif user.auth_provider == 'local':
                    # Update auth provider to indicate Google is now linked
                    # We keep it as 'local' but the social account will be linked
                    if user_info.get('picture') and not user.profile_picture:
                        user.profile_picture = user_info.get('picture')
                    if user_info.get('name') and not user.full_name:
                        user.full_name = user_info.get('name')
                    user.save()
                    
                    # Create or update social account
                    social_account, created = SocialAccount.objects.get_or_create(
                        user=user,
                        provider='google',
                        defaults={
                            'uid': user_info.get('sub'),
                            'extra_data': user_info,
                        }
                    )
                    if not created:
                        social_account.extra_data = user_info
                        social_account.save()
                    
                    log_user_activity(user, 'google_account_linked', {
                        'email': email,
                    })
                
                log_user_activity(user, 'google_login', {
                    'email': email,
                    'auth_provider': user.auth_provider,
                })
                
            except User.DoesNotExist:
                # Create new user with Google auth
                user = User.objects.create_user(
                    email=email,
                    password=None,  # No password for Google users
                    full_name=user_info.get('name', ''),
                    auth_provider='google',
                    profile_picture=user_info.get('picture', ''),
                    onboarding_completed=False,
                    role='user',
                    # user_type='explorer'
                )
                
                # Create social account
                SocialAccount.objects.create(
                    user=user,
                    provider='google',
                    uid=user_info.get('sub'),
                    extra_data=user_info,
                )
                
                log_user_activity(user, 'google_register', {
                    'email': email,
                })

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            jwt_access_token = str(refresh.access_token)

            # Update last login
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])

            return Response({
                'access_token': jwt_access_token,
                'refresh_token': str(refresh),
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'full_name': user.full_name,
                    'role': user.role,
                    'onboarding_completed': user.onboarding_completed,
                    'auth_provider': user.auth_provider,
                    'profile_picture': user.profile_picture,
                }
            })

        except Exception as e:
            logger.error("Google OAuth error: %s", str(e), exc_info=True)
            return Response(
                {'error': 'Authentication failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GoogleAuthConfigView(APIView):
    """
    Return Google OAuth configuration for the frontend.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from django.conf import settings
        
        return Response({
            'google_client_id': settings.GOOGLE_CLIENT_ID,
            'enabled': bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET),
        })
