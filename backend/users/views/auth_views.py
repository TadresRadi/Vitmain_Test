"""
Authentication views.
Handles login, registration, and OAuth flows.
"""
import logging
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.conf import settings
from core.timing_safe import RandomDelay
from core.audit_service import get_audit_logger

from users.serializers import (
    GoogleAuthCallbackSerializer,
    UserDetailSerializer,
)
from users.services import GoogleAuthService
from core.exceptions import AuthenticationError, ExternalServiceError, ValidationError
from core.decorators import rate_limit
from core.decorators import ratelimit

logger = logging.getLogger(__name__)


class MyTokenObtainPairView(TokenObtainPairView):
    """
    Login view - exchange email/password for JWT tokens.
    
    POST /api/auth/login
    {
        "email": "user@example.com",
        "password": "password"
    }
    """
    pass


class RegisterView(APIView):
    """
    User registration view.
    
    POST /api/auth/register
    {
        "email": "user@example.com",
        "password": "password",
        "full_name": "Full Name"
    }
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Register new user."""
        # Validation would be done by serializer
        pass


class GoogleOAuthCallbackView(APIView):
    """
    Handle Google OAuth callback and return JWT tokens.
    
    POST /api/auth/google/callback
    {
        "id_token": "google_id_token_string"
    }
    
    Response:
    {
        "access_token": "jwt_access_token",
        "refresh_token": "jwt_refresh_token",
        "user": {...}
    }
    """
    permission_classes = [permissions.AllowAny]
    
    @ratelimit(key='ip', rate='10/m')
    def post(self, request):
        """
        Authenticate user with Google OAuth token.
        """
        # Validate request
        serializer = GoogleAuthCallbackSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(str(serializer.errors))
        
        token = serializer.validated_data['token']
        
        try:
            # Initialize service
            google_auth_service = GoogleAuthService()
            
            # Verify token with Google
            user_info = google_auth_service.verify_id_token(token)
            if not user_info:
                logger.warning("Invalid Google token provided")
                raise AuthenticationError("Invalid or expired Google token")
            
            email = user_info.get('email')
            if not email:
                logger.error("Google token missing email after verification")
                raise AuthenticationError("Invalid Google token")
            
            # Authenticate or create user
            user, created = google_auth_service.authenticate_user(email, user_info)
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            jwt_access = str(refresh.access_token)
            
            # Update last login
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            # Serialize response
            user_serializer = UserDetailSerializer(user)
            response_data = {
                'access_token': jwt_access,
                'refresh_token': str(refresh),
                'user': user_serializer.data,
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except AuthenticationError:
            raise
        except ExternalServiceError:
            raise
        except ValidationError:
            raise
        except Exception as e:
            logger.exception("Unexpected error in Google OAuth callback")
            raise ExternalServiceError("Authentication failed")


class GoogleAuthConfigView(APIView):
    """
    Return Google OAuth configuration for frontend.
    Cached for 1 hour.
    
    GET /api/auth/google/config
    
    Response:
    {
        "google_client_id": "client_id.apps.googleusercontent.com",
        "enabled": true
    }
    """
    permission_classes = [permissions.AllowAny]
    
    @method_decorator(cache_page(3600))
    def get(self, request):
        """Get Google OAuth configuration."""
        return Response({
            'google_client_id': settings.GOOGLE_CLIENT_ID,
            'enabled': bool(
                settings.GOOGLE_CLIENT_ID and 
                settings.GOOGLE_CLIENT_SECRET
            ),
        })

class LogoutView(APIView):
    """
    Logout user by blacklisting tokens.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Logout user and blacklist tokens."""
        audit_logger = get_audit_logger()
        user_ip = self._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        try:
            from users.services.token_service import get_token_service
            
            token_service = get_token_service()
            
            # Get refresh token from request
            refresh_token = request.data.get('refresh_token')
            
            # Blacklist access token from Authorization header
            auth_header = request.META.get('HTTP_AUTHORIZATION', '').split()
            if len(auth_header) == 2 and auth_header[0] == 'Bearer':
                access_token = auth_header[1]
                token_service.blacklist_token(access_token)
            
            # Blacklist refresh token
            if refresh_token:
                token_service.blacklist_token(refresh_token)
            
            # Log logout
            audit_logger.log_logout(
                user=request.user,
                user_ip=user_ip,
                user_agent=user_agent,
            )
            
            log_user_activity(request.user, 'user_logout', {
                'timestamp': timezone.now().isoformat()
            })
            
            return Response(
                {'message': 'Successfully logged out'},
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            logger.exception("Logout error")
            raise ExternalServiceError("Logout failed")

    @staticmethod
    def _get_client_ip(request) -> str:
        """Get client IP."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')
        try:
            from users.services.token_service import get_token_service
            
            token_service = get_token_service()
            
            # Get refresh token from request
            refresh_token = request.data.get('refresh_token')
            
            # Blacklist access token from Authorization header
            auth_header = request.META.get('HTTP_AUTHORIZATION', '').split()
            if len(auth_header) == 2 and auth_header[0] == 'Bearer':
                access_token = auth_header[1]
                token_service.blacklist_token(access_token)
            
            # Blacklist refresh token
            if refresh_token:
                token_service.blacklist_token(refresh_token)
            
            return Response(
                {'message': 'Successfully logged out'},
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            logger.exception("Logout error")
            raise ExternalServiceError("Logout failed")
        
class MyTokenObtainPairView(TokenObtainPairView):
    """Login view with rate limiting."""
    
    @rate_limit(endpoint='auth_login', rate='5/m')
    def post(self, request, *args, **kwargs):
        audit_logger = get_audit_logger()
        user_ip = self._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        try:
            response = super().post(request, *args, **kwargs)
            
            # Log successful login
            email = request.data.get('email', 'unknown')
            audit_logger.log_authentication(
                user_email=email,
                success=True,
                auth_method='local',
                user_ip=user_ip,
                user_agent=user_agent,
            )
            
            return response
        except Exception as e:
            # Log failed login
            email = request.data.get('email', 'unknown')
            audit_logger.log_authentication(
                user_email=email,
                success=False,
                auth_method='local',
                user_ip=user_ip,
                user_agent=user_agent,
                error_message=str(e),
            )
            raise

    @staticmethod
    def _get_client_ip(request) -> str:
        """Get client IP."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')

class RegisterView(APIView):
    """Registration view with rate limiting."""
    permission_classes = [permissions.AllowAny]
    
    @rate_limit(endpoint='auth_register', rate='3/h')
    def post(self, request):
        # Registration logic
        pass


class GoogleOAuthCallbackView(APIView):
    """Google OAuth callback with rate limiting."""
    permission_classes = [permissions.AllowAny]
    
    @rate_limit(endpoint='google_callback', rate='10/m')
    def post(self, request):
        # OAuth logic
        pass


class LogoutView(APIView):
    """Logout with rate limiting."""
    permission_classes = [permissions.IsAuthenticated]
    
    @rate_limit(endpoint='auth_logout', rate='10/m')
    def post(self, request):
        # Logout logic
        pass    