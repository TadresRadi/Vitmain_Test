"""
Core models for the application.
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField

User = get_user_model()


class AuditLog(models.Model):
    """
    Audit log for tracking all important events.
    Used for compliance, security monitoring, and forensics.
    """

    # Event categories
    EVENT_CATEGORIES = [
        ('authentication', 'Authentication'),
        ('authorization', 'Authorization'),
        ('data_access', 'Data Access'),
        ('data_modification', 'Data Modification'),
        ('data_deletion', 'Data Deletion'),
        ('security', 'Security Event'),
        ('system', 'System Event'),
        ('error', 'Error'),
    ]

    # Event severity levels
    SEVERITY_LEVELS = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]

    # Event actions
    EVENT_ACTIONS = [
        # Authentication
        ('login_success', 'Login Success'),
        ('login_failure', 'Login Failure'),
        ('logout', 'Logout'),
        ('oauth_login', 'OAuth Login'),
        ('password_changed', 'Password Changed'),
        ('password_reset', 'Password Reset'),
        ('token_refresh', 'Token Refresh'),
        ('token_revoked', 'Token Revoked'),

        # Authorization
        ('permission_denied', 'Permission Denied'),
        ('role_changed', 'Role Changed'),

        # Data Access
        ('data_accessed', 'Data Accessed'),
        ('report_generated', 'Report Generated'),

        # Data Modification
        ('data_created', 'Data Created'),
        ('data_updated', 'Data Updated'),

        # Data Deletion
        ('data_deleted', 'Data Deleted'),
        ('account_deleted', 'Account Deleted'),

        # Security
        ('suspicious_activity', 'Suspicious Activity'),
        ('rate_limit_exceeded', 'Rate Limit Exceeded'),
        ('invalid_csrf', 'Invalid CSRF'),
        ('account_locked', 'Account Locked'),

        # System
        ('system_error', 'System Error'),
        ('configuration_changed', 'Configuration Changed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # User info
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    user_email = models.EmailField(max_length=254, db_index=True)
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    # Event details
    event_category = models.CharField(
        max_length=50,
        choices=EVENT_CATEGORIES,
        db_index=True
    )
    event_action = models.CharField(
        max_length=50,
        choices=EVENT_ACTIONS,
        db_index=True
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_LEVELS,
        default='info',
        db_index=True
    )

    # Event data
    description = models.TextField(blank=True)
    resource_type = models.CharField(max_length=100, blank=True, db_index=True)
    resource_id = models.CharField(max_length=255, blank=True, db_index=True)
    
    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True)
    error_details = models.JSONField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    # Status codes
    status_code = models.IntegerField(null=True, blank=True)
    success = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['event_action', '-created_at']),
            models.Index(fields=['severity', '-created_at']),
            models.Index(fields=['user_email', '-created_at']),
            models.Index(fields=['resource_type', 'resource_id']),
        ]
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'

    def __str__(self):
        return f"{self.event_action} - {self.user_email} - {self.created_at}"

    @classmethod
    def log_event(
        cls,
        user: User = None,
        user_email: str = None,
        event_category: str = 'system',
        event_action: str = 'system_event',
        severity: str = 'info',
        description: str = '',
        resource_type: str = '',
        resource_id: str = '',
        metadata: dict = None,
        status_code: int = None,
        success: bool = True,
        user_ip: str = None,
        user_agent: str = None,
        error_details: dict = None,
    ) -> 'AuditLog':
        """
        Create an audit log entry.

        Args:
            user: User instance
            user_email: User email (if user not available)
            event_category: Category of event
            event_action: Specific action
            severity: Severity level
            description: Human-readable description
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            metadata: Additional metadata
            status_code: HTTP status code
            success: Whether operation succeeded
            user_ip: User IP address
            user_agent: User agent string
            error_details: Error information

        Returns:
            Created AuditLog instance
        """
        if user:
            user_email = user.email
        elif not user_email:
            user_email = 'unknown'

        audit_log = cls.objects.create(
            user=user,
            user_email=user_email,
            user_ip=user_ip,
            user_agent=user_agent,
            event_category=event_category,
            event_action=event_action,
            severity=severity,
            description=description,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata or {},
            status_code=status_code,
            success=success,
            error_details=error_details,
        )

        return audit_log