"""
Password management views.
Handles password change, reset, and recovery flows.
"""
import logging
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils import timezone

from users.serializers import PasswordChangeSerializer
from users.services.password_service import (
    PasswordService,
    get_password_service,
)
from core.email_service import get_email_service
from core.exceptions import ValidationError, AuthenticationError
from core.decorators import rate_limit
from core.utils import log_user_activity
from core.audit_service import get_audit_logger

User = get_user_model()
logger = logging.getLogger(__name__)


class PasswordChangeView(APIView):
    """Change password for authenticated user."""
    permission_classes = [permissions.IsAuthenticated]
    
    @rate_limit(endpoint='password_change', rate='3/h')
    def post(self, request):
        """Change user password."""
        audit_logger = get_audit_logger()
        user_ip = self._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
    @staticmethod
    def _get_client_ip(request) -> str:
        """Get client IP."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')

        try:
            # Validate request data
            serializer = PasswordChangeSerializer(data=request.data)
            if not serializer.is_valid():
                raise ValidationError(str(serializer.errors))
            
            # Get validated data
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            
            # Use service to change password
            password_service = get_password_service()
            success, message = password_service.change_password(
                user=request.user,
                old_password=old_password,
                new_password=new_password
            )
            
            if not success:
                raise AuthenticationError(message)
            
            # Send confirmation email
            email_service = get_email_service()
            email_service.send_password_change_confirmation(request.user.email)
            
            return Response(
                {'message': message},
                status=status.HTTP_200_OK
            )
        
        except ValidationError:
            raise
        except AuthenticationError:
            raise
        except Exception as e:
            logger.exception("Password change error")
            raise ValidationError("Failed to change password")


class PasswordResetRequestView(APIView):
    """
    Request password reset.
    Sends reset link via email.
    
    POST /api/auth/password/reset-request
    {
        "email": "user@example.com"
    }
    """
    permission_classes = [permissions.AllowAny]
    
    @rate_limit(endpoint='password_reset_request', rate='3/h')
    def post(self, request):
        """Request password reset."""
        from core.constant_response import ConstantResponse
        from core.timing_safe import RandomDelay
        
        try:
            email = request.data.get('email', '').strip().lower()
            
            if not email or '@' not in email:
                # Add delay even for invalid email format
                RandomDelay.add_delay(100, 200)
                return Response(
                    ConstantResponse.password_reset_response(),
                    status=status.HTTP_200_OK
                )
            
            # Use service to initiate reset
            password_service = get_password_service()
            success, message, reset_token = password_service.initiate_password_reset(email)
            
            if success and reset_token:
                # Send reset email
                email_service = get_email_service()
                frontend_url = request.META.get('HTTP_ORIGIN', 'http://localhost:5173')
                
                email_sent = email_service.send_password_reset_email(
                    user_email=email,
                    reset_token=reset_token,
                    frontend_url=frontend_url
                )
                
                if not email_sent:
                    logger.warning(f"Failed to send reset email to: {email}")
            
            # Add small random delay to prevent timing attacks
            RandomDelay.add_delay(100, 300)
            
            # Always return same message (don't reveal if user exists)
            return Response(
                ConstantResponse.password_reset_response(),
                status=status.HTTP_200_OK
            )
        
        except ValidationError:
            raise
        except Exception as e:
            logger.exception("Password reset request error")
            # Add delay on error too
            RandomDelay.add_delay(100, 300)
            return Response(
                ConstantResponse.password_reset_response(),
                status=status.HTTP_200_OK
            )

class PasswordResetView(APIView):
    """
    Complete password reset with token.
    
    POST /api/auth/password/reset
    {
        "email": "user@example.com",
        "token": "reset_token_from_email",
        "new_password": "new_secure_password"
    }
    """
    permission_classes = [permissions.AllowAny]
    
    @rate_limit(endpoint='password_reset', rate='5/h')
    def post(self, request):
        """Reset password with token."""
        from core.timing_safe import RandomDelay
        
        try:
            email = request.data.get('email', '').strip().lower()
            token = request.data.get('token', '').strip()
            new_password = request.data.get('new_password', '')
            
            # Validate inputs
            if not email or '@' not in email:
                RandomDelay.add_delay(100, 300)
                raise AuthenticationError("Invalid or expired reset token")
            
            if not token:
                RandomDelay.add_delay(100, 300)
                raise AuthenticationError("Invalid or expired reset token")
            
            if not new_password:
                RandomDelay.add_delay(100, 300)
                raise AuthenticationError("Invalid or expired reset token")
            
            # Validate password strength (add delay before checking)
            password_service = get_password_service()
            is_secure, error = password_service.is_password_secure(new_password)
            if not is_secure:
                RandomDelay.add_delay(100, 300)
                raise AuthenticationError("Invalid or expired reset token")
            
            # Use service to reset password
            success, message = password_service.reset_password(
                email=email,
                token=token,
                new_password=new_password
            )
            
            if not success:
                # Add delay on failure
                RandomDelay.add_delay(200, 400)
                raise AuthenticationError("Invalid or expired reset token")
            
            # Add delay on success too (to prevent timing differences)
            RandomDelay.add_delay(200, 400)
            
            return Response(
                {'message': 'Password reset successfully'},
                status=status.HTTP_200_OK
            )
        
        except AuthenticationError:
            raise
        except Exception as e:
            logger.exception("Password reset error")
            RandomDelay.add_delay(200, 400)
            raise AuthenticationError("Invalid or expired reset token")

class PasswordStrengthCheckView(APIView):
    """
    Check password strength without changing it.
    Helps users validate password before submission.
    
    POST /api/auth/password/check-strength
    {
        "password": "password_to_check"
    }
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Check password strength."""
        try:
            password = request.data.get('password', '')
            
            if not password:
                raise ValidationError("Password is required")
            
            password_service = get_password_service()
            is_secure, error = password_service.is_password_secure(password)
            
            if is_secure:
                return Response(
                    {
                        'secure': True,
                        'message': 'Password is strong'
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        'secure': False,
                        'message': error,
                        'requirements': [
                            'At least 8 characters',
                            'At least one uppercase letter',
                            'At least one lowercase letter',
                            'At least one digit',
                            'At least one special character (!@#$%^&*)',
                        ]
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        except ValidationError:
            raise
        except Exception as e:
            logger.exception("Password strength check error")
            raise ValidationError("Error checking password strength")