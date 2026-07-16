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
from core.audit_service import get_audit_logger

from users.serializers import (
    GoogleAuthCallbackSerializer,
    MyTokenObtainPairSerializer,
    UserDetailSerializer,
)
from users.services import GoogleAuthService
from core.services import ServiceException
from core.exceptions import AuthenticationError, ExternalServiceError, ValidationError
from core.decorators import rate_limit
from core.utils import log_user_activity
from core.http_utils import get_client_ip

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
    serializer_class = MyTokenObtainPairSerializer

    @rate_limit(endpoint='auth_login', rate='5/m')
    def post(self, request, *args, **kwargs):
        audit_logger = get_audit_logger()
        user_ip = get_client_ip(request)
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

    @rate_limit(endpoint='auth_register', rate='3/h')
    def post(self, request):
        from users.serializers import RegisterSerializer
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        log_user_activity(user, 'user_registered_local', {
            'email': user.email,
        })

        return Response({'message': 'Registration successful'}, status=status.HTTP_201_CREATED)


class GoogleOAuthCallbackView(APIView):
    """
    Handle Google OAuth callback and return JWT tokens.
    
    POST /auth/google/callback
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
    
    @rate_limit(endpoint='google_callback', rate='10/m')
    def post(self, request):
        """
        Authenticate user with Google OAuth token.
        """
        try:
            # Validate request
            serializer = GoogleAuthCallbackSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {'error': 'Invalid token format', 'detail': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = serializer.validated_data['token']
            
            # Initialize service
            google_auth_service = GoogleAuthService()
            
            # Verify token with Google
            user_info = google_auth_service.verify_id_token(token)
            if not user_info:
                logger.warning("Invalid Google token provided")
                return Response(
                    {'error': 'Invalid or expired Google token'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            email = user_info.get('email')
            if not email:
                logger.error("Google token missing email after verification")
                return Response(
                    {'error': 'Invalid Google token - missing email'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Authenticate or create user
            user, created = google_auth_service.authenticate_user(email, user_info)
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            jwt_access = str(refresh.access_token)
            
            # Update last login
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            # Log successful authentication
            audit_logger = get_audit_logger()
            user_ip = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            audit_logger.log_authentication(
                user_email=email,
                success=True,
                auth_method='google',
                user_ip=user_ip,
                user_agent=user_agent,
            )
            
            # Serialize response
            user_serializer = UserDetailSerializer(user)
            response_data = {
                'access_token': jwt_access,
                'refresh_token': str(refresh),
                'user': user_serializer.data,
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except AuthenticationError as e:
            logger.warning(f"Authentication error: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except ServiceException as e:
            # Service-level failures (Google API timeout, config errors, etc.)
            # should return 503, not 500.
            logger.error(f"Service error in Google OAuth: {str(e)}")
            return Response(
                {'error': 'Authentication service unavailable'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except ExternalServiceError as e:
            logger.error(f"External service error: {str(e)}")
            return Response(
                {'error': 'Authentication service unavailable'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except ValidationError as e:
            logger.warning(f"Validation error: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception("Unexpected error in Google OAuth callback")
            return Response(
                {'error': 'Authentication failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GoogleAuthConfigView(APIView):
    """
    Return Google OAuth configuration for frontend.
    Cached for 1 hour.
    
    GET /auth/google/config
    
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
            'enabled': bool(settings.GOOGLE_CLIENT_ID),
        })

class LogoutView(APIView):
    """
    Logout user by blacklisting tokens.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Logout user and blacklist tokens."""
        audit_logger = get_audit_logger()
        user_ip = get_client_ip(request)
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
