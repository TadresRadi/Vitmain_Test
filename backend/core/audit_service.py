"""
Audit logging service.
Centralized audit event tracking.
"""
import logging
from typing import Optional, Dict, Any
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import AuditLog

User = get_user_model()
logger = logging.getLogger(__name__)


class AuditLogger:
    """Service for logging audit events."""

    @staticmethod
    def log_authentication(
        user_email: str,
        success: bool,
        auth_method: str = 'local',
        user_ip: str = None,
        user_agent: str = None,
        error_message: str = None,
    ) -> AuditLog:
        """
        Log authentication attempt.

        Args:
            user_email: User email
            success: Whether login succeeded
            auth_method: Authentication method (local, google, etc.)
            user_ip: Client IP
            user_agent: User agent string
            error_message: Error message if failed

        Returns:
            Created AuditLog
        """
        try:
            user = User.objects.filter(email=user_email).first()

            event_action = 'login_success' if success else 'login_failure'
            severity = 'info' if success else 'warning'

            metadata = {
                'auth_method': auth_method,
                'timestamp': timezone.now().isoformat(),
            }

            error_details = None
            if error_message:
                error_details = {'message': error_message}

            return AuditLog.log_event(
                user=user,
                user_email=user_email,
                event_category='authentication',
                event_action=event_action,
                severity=severity,
                description=f"{auth_method.capitalize()} login {'successful' if success else 'failed'}",
                metadata=metadata,
                success=success,
                user_ip=user_ip,
                user_agent=user_agent,
                error_details=error_details,
            )
        except Exception as e:
            logger.error(f"Error logging authentication: {str(e)}")
            raise

    @staticmethod
    def log_logout(
        user: User,
        user_ip: str = None,
        user_agent: str = None,
    ) -> AuditLog:
        """
        Log user logout.

        Args:
            user: User instance
            user_ip: Client IP
            user_agent: User agent string

        Returns:
            Created AuditLog
        """
        try:
            return AuditLog.log_event(
                user=user,
                user_email=user.email,
                event_category='authentication',
                event_action='logout',
                severity='info',
                description='User logged out',
                metadata={
                    'timestamp': timezone.now().isoformat(),
                },
                success=True,
                user_ip=user_ip,
                user_agent=user_agent,
            )
        except Exception as e:
            logger.error(f"Error logging logout: {str(e)}")
            raise

    @staticmethod
    def log_password_change(
        user: User,
        user_ip: str = None,
        user_agent: str = None,
    ) -> AuditLog:
        """
        Log password change.

        Args:
            user: User instance
            user_ip: Client IP
            user_agent: User agent string

        Returns:
            Created AuditLog
        """
        try:
            return AuditLog.log_event(
                user=user,
                user_email=user.email,
                event_category='security',
                event_action='password_changed',
                severity='info',
                description='User changed password',
                metadata={
                    'timestamp': timezone.now().isoformat(),
                },
                success=True,
                user_ip=user_ip,
                user_agent=user_agent,
            )
        except Exception as e:
            logger.error(f"Error logging password change: {str(e)}")
            raise

    @staticmethod
    def log_permission_denied(
        user: User,
        resource_type: str,
        resource_id: str,
        user_ip: str = None,
        user_agent: str = None,
    ) -> AuditLog:
        """
        Log unauthorized access attempt.

        Args:
            user: User instance
            resource_type: Type of resource
            resource_id: ID of resource
            user_ip: Client IP
            user_agent: User agent string

        Returns:
            Created AuditLog
        """
        try:
            return AuditLog.log_event(
                user=user,
                user_email=user.email if user else 'unknown',
                event_category='authorization',
                event_action='permission_denied',
                severity='warning',
                description=f"Access denied to {resource_type}",
                resource_type=resource_type,
                resource_id=resource_id,
                metadata={
                    'timestamp': timezone.now().isoformat(),
                },
                success=False,
                user_ip=user_ip,
                user_agent=user_agent,
            )
        except Exception as e:
            logger.error(f"Error logging permission denied: {str(e)}")
            raise

    @staticmethod
    def log_suspicious_activity(
        user: User = None,
        user_email: str = None,
        activity_type: str = '',
        description: str = '',
        user_ip: str = None,
        user_agent: str = None,
    ) -> AuditLog:
        """
        Log suspicious activity.

        Args:
            user: User instance
            user_email: User email
            activity_type: Type of suspicious activity
            description: Description of activity
            user_ip: Client IP
            user_agent: User agent string

        Returns:
            Created AuditLog
        """
        try:
            return AuditLog.log_event(
                user=user,
                user_email=user_email or (user.email if user else 'unknown'),
                event_category='security',
                event_action='suspicious_activity',
                severity='critical',
                description=description or f"Suspicious activity detected: {activity_type}",
                metadata={
                    'activity_type': activity_type,
                    'timestamp': timezone.now().isoformat(),
                },
                success=False,
                user_ip=user_ip,
                user_agent=user_agent,
            )
        except Exception as e:
            logger.error(f"Error logging suspicious activity: {str(e)}")
            raise

    @staticmethod
    def log_rate_limit_exceeded(
        user_email: str,
        endpoint: str,
        user_ip: str = None,
        user_agent: str = None,
    ) -> AuditLog:
        """
        Log rate limit exceeded.

        Args:
            user_email: User email or IP
            endpoint: API endpoint
            user_ip: Client IP
            user_agent: User agent string

        Returns:
            Created AuditLog
        """
        try:
            return AuditLog.log_event(
                user_email=user_email,
                event_category='security',
                event_action='rate_limit_exceeded',
                severity='warning',
                description=f"Rate limit exceeded on {endpoint}",
                metadata={
                    'endpoint': endpoint,
                    'timestamp': timezone.now().isoformat(),
                },
                success=False,
                user_ip=user_ip,
                user_agent=user_agent,
            )
        except Exception as e:
            logger.error(f"Error logging rate limit: {str(e)}")
            raise

    @staticmethod
    def log_data_access(
        user: User,
        resource_type: str,
        resource_id: str,
        user_ip: str = None,
        user_agent: str = None,
    ) -> AuditLog:
        """
        Log data access.

        Args:
            user: User instance
            resource_type: Type of resource accessed
            resource_id: ID of resource
            user_ip: Client IP
            user_agent: User agent string

        Returns:
            Created AuditLog
        """
        try:
            return AuditLog.log_event(
                user=user,
                user_email=user.email,
                event_category='data_access',
                event_action='data_accessed',
                severity='info',
                description=f"Accessed {resource_type}",
                resource_type=resource_type,
                resource_id=resource_id,
                metadata={
                    'timestamp': timezone.now().isoformat(),
                },
                success=True,
                user_ip=user_ip,
                user_agent=user_agent,
            )
        except Exception as e:
            logger.error(f"Error logging data access: {str(e)}")
            raise

    @staticmethod
    def log_system_error(
        error_message: str,
        error_type: str = 'Unknown',
        user: User = None,
        user_ip: str = None,
        user_agent: str = None,
    ) -> AuditLog:
        """
        Log system error.

        Args:
            error_message: Error message
            error_type: Type of error
            user: User instance
            user_ip: Client IP
            user_agent: User agent string

        Returns:
            Created AuditLog
        """
        try:
            return AuditLog.log_event(
                user=user,
                user_email=user.email if user else 'system',
                event_category='error',
                event_action='system_error',
                severity='critical',
                description=error_message,
                metadata={
                    'error_type': error_type,
                    'timestamp': timezone.now().isoformat(),
                },
                success=False,
                user_ip=user_ip,
                user_agent=user_agent,
                error_details={'type': error_type, 'message': error_message},
            )
        except Exception as e:
            logger.error(f"Error logging system error: {str(e)}")
            raise


# Singleton instance
_audit_logger = None


def get_audit_logger() -> AuditLogger:
    """Get audit logger singleton."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger