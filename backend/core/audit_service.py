"""
Audit logging service.
Centralized audit event tracking.
"""
import logging
from typing import Optional
from typing import Any

from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import AuditLog

User = get_user_model()
logger = logging.getLogger(__name__)


class AuditLogger:
    """Service for logging audit events against the active AuditLog model."""

    @staticmethod
    def _create_log(
        action: str,
        user: User = None,
        user_email: str = None,
        **details: Any,
    ) -> Optional[AuditLog]:
        if user is None and user_email:
            user = User.objects.filter(email=user_email).first()

        if user is None:
            logger.info("Audit event without local user: %s %s", action, details)
            return None

        details = {key: value for key, value in details.items() if value is not None}
        details.setdefault("user_email", user_email or user.email)
        details.setdefault("timestamp", timezone.now().isoformat())
        return AuditLog.objects.create(user=user, action=action, details=details)

    @staticmethod
    def log_authentication(
        user_email: str,
        success: bool,
        auth_method: str = "local",
        user_ip: str = None,
        user_agent: str = None,
        error_message: str = None,
    ) -> Optional[AuditLog]:
        try:
            return AuditLogger._create_log(
                action="login_success" if success else "login_failure",
                user_email=user_email,
                event_category="authentication",
                severity="info" if success else "warning",
                auth_method=auth_method,
                success=success,
                user_ip=user_ip,
                user_agent=user_agent,
                error_message=error_message,
            )
        except Exception:
            logger.exception("Error logging authentication")
            return None

    @staticmethod
    def log_logout(
        user: User,
        user_ip: str = None,
        user_agent: str = None,
    ) -> Optional[AuditLog]:
        try:
            return AuditLogger._create_log(
                action="logout",
                user=user,
                event_category="authentication",
                severity="info",
                description="User logged out",
                success=True,
                user_ip=user_ip,
                user_agent=user_agent,
            )
        except Exception:
            logger.exception("Error logging logout")
            return None

    @staticmethod
    def log_password_change(
        user: User,
        user_ip: str = None,
        user_agent: str = None,
    ) -> Optional[AuditLog]:
        try:
            return AuditLogger._create_log(
                action="password_changed",
                user=user,
                event_category="security",
                severity="info",
                description="User changed password",
                success=True,
                user_ip=user_ip,
                user_agent=user_agent,
            )
        except Exception:
            logger.exception("Error logging password change")
            return None

    @staticmethod
    def log_permission_denied(
        user: User,
        resource_type: str,
        resource_id: str,
        user_ip: str = None,
        user_agent: str = None,
    ) -> Optional[AuditLog]:
        try:
            return AuditLogger._create_log(
                action="permission_denied",
                user=user,
                user_email=user.email if user else None,
                event_category="authorization",
                severity="warning",
                description=f"Access denied to {resource_type}",
                resource_type=resource_type,
                resource_id=resource_id,
                success=False,
                user_ip=user_ip,
                user_agent=user_agent,
            )
        except Exception:
            logger.exception("Error logging permission denied")
            return None

    @staticmethod
    def log_suspicious_activity(
        user: User = None,
        user_email: str = None,
        activity_type: str = "",
        description: str = "",
        user_ip: str = None,
        user_agent: str = None,
    ) -> Optional[AuditLog]:
        try:
            return AuditLogger._create_log(
                action="suspicious_activity",
                user=user,
                user_email=user_email or (user.email if user else None),
                event_category="security",
                severity="critical",
                description=description or f"Suspicious activity detected: {activity_type}",
                activity_type=activity_type,
                success=False,
                user_ip=user_ip,
                user_agent=user_agent,
            )
        except Exception:
            logger.exception("Error logging suspicious activity")
            return None

    @staticmethod
    def log_rate_limit_exceeded(
        user_email: str,
        endpoint: str,
        user_ip: str = None,
        user_agent: str = None,
    ) -> Optional[AuditLog]:
        try:
            return AuditLogger._create_log(
                action="rate_limit_exceeded",
                user_email=user_email,
                event_category="security",
                severity="warning",
                description=f"Rate limit exceeded on {endpoint}",
                endpoint=endpoint,
                success=False,
                user_ip=user_ip,
                user_agent=user_agent,
            )
        except Exception:
            logger.exception("Error logging rate limit")
            return None

    @staticmethod
    def log_data_access(
        user: User,
        resource_type: str,
        resource_id: str,
        user_ip: str = None,
        user_agent: str = None,
    ) -> Optional[AuditLog]:
        try:
            return AuditLogger._create_log(
                action="data_accessed",
                user=user,
                event_category="data_access",
                severity="info",
                description=f"Accessed {resource_type}",
                resource_type=resource_type,
                resource_id=resource_id,
                success=True,
                user_ip=user_ip,
                user_agent=user_agent,
            )
        except Exception:
            logger.exception("Error logging data access")
            return None

    @staticmethod
    def log_system_error(
        error_message: str,
        error_type: str = "Unknown",
        user: User = None,
        user_ip: str = None,
        user_agent: str = None,
    ) -> Optional[AuditLog]:
        try:
            return AuditLogger._create_log(
                action="system_error",
                user=user,
                user_email=user.email if user else None,
                event_category="error",
                severity="critical",
                description=error_message,
                error_type=error_type,
                success=False,
                user_ip=user_ip,
                user_agent=user_agent,
                error_message=error_message,
            )
        except Exception:
            logger.exception("Error logging system error")
            return None


_audit_logger = None


def get_audit_logger() -> AuditLogger:
    """Get audit logger singleton."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger
