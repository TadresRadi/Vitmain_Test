"""
API Key models for managing third-party integrations.
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class APIKey(models.Model):
    """
    API Key for programmatic access.
    Used by third-party services and mobile apps.
    """

    # Scopes - what this key can access
    SCOPE_CHOICES = [
        ('read', 'Read Only'),
        ('write', 'Write'),
        ('admin', 'Admin'),
    ]

    # Status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('revoked', 'Revoked'),
        ('expired', 'Expired'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Owner info
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='api_keys'
    )
    
    # Key details
    name = models.CharField(max_length=255, help_text='Friendly name for this key')
    key_prefix = models.CharField(
        max_length=32,
        unique=True,
        db_index=True,
        editable=False,
        help_text='First 32 chars of key (for identification)'
    )
    key_hash = models.CharField(
        max_length=255,
        editable=False,
        help_text='SHA256 hash of full key'
    )
    
    # Permissions
    scope = models.CharField(
        max_length=20,
        choices=SCOPE_CHOICES,
        default='read'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True
    )
    
    # Expiry
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text='Leave blank for never expires'
    )
    
    # Usage tracking
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Last time this key was used'
    )
    last_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='Last IP that used this key'
    )
    
    # Metadata
    description = models.TextField(
        blank=True,
        help_text='Optional description of what this key is used for'
    )
    allowed_ips = models.JSONField(
        default=list,
        blank=True,
        help_text='List of IPs allowed to use this key (empty = all)'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    rotated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When this key was rotated'
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['key_prefix']),
        ]
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'

    def __str__(self):
        return f"{self.name} ({self.key_prefix}...)"

    def is_valid(self) -> bool:
        """
        Check if key is valid for use.
        
        Returns:
            True if key is active and not expired
        """
        if self.status != 'active':
            return False
        
        if self.expires_at and timezone.now() > self.expires_at:
            self.status = 'expired'
            self.save(update_fields=['status'])
            return False
        
        return True

    def is_ip_allowed(self, ip: str) -> bool:
        """
        Check if IP is allowed to use this key.
        
        Args:
            ip: IP address to check
        
        Returns:
            True if IP is allowed
        """
        if not self.allowed_ips:
            return True  # No restrictions
        
        return ip in self.allowed_ips

    def update_last_used(self, ip: str = None) -> None:
        """
        Update last used timestamp.
        
        Args:
            ip: IP address that used the key
        """
        self.last_used_at = timezone.now()
        if ip:
            self.last_ip = ip
        self.save(update_fields=['last_used_at', 'last_ip'])


class APIKeyAuditLog(models.Model):
    """
    Audit log for API key usage and management.
    """

    # Event types
    EVENT_TYPES = [
        ('created', 'Created'),
        ('used', 'Used'),
        ('rotated', 'Rotated'),
        ('revoked', 'Revoked'),
        ('expired', 'Expired'),
        ('ip_blocked', 'IP Blocked'),
        ('rate_limit', 'Rate Limited'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Reference
    api_key = models.ForeignKey(
        APIKey,
        on_delete=models.CASCADE,
        related_name='audit_logs'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='api_key_audit_logs'
    )
    
    # Event
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPES,
        db_index=True
    )
    description = models.TextField(blank=True)
    
    # Request info
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    endpoint = models.CharField(
    max_length=255,
    blank=True,
    null=True,
        )
    status_code = models.IntegerField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['api_key', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['event_type', '-created_at']),
        ]
        verbose_name = 'API Key Audit Log'
        verbose_name_plural = 'API Key Audit Logs'

    def __str__(self):
        return f"{self.api_key.name} - {self.event_type}"

    @classmethod
    def log_event(
        cls,
        api_key: APIKey,
        event_type: str,
        user: User = None,
        ip_address: str = None,
        endpoint: str = None,
        status_code: int = None,
        description: str = '',
        metadata: dict = None,
    ) -> 'APIKeyAuditLog':
        """
        Create an API key audit log entry.
        
        Args:
            api_key: APIKey instance
            event_type: Type of event
            user: User instance
            ip_address: IP address
            endpoint: API endpoint accessed
            status_code: HTTP status code
            description: Event description
            metadata: Additional metadata
        
        Returns:
            Created APIKeyAuditLog instance
        """
        return cls.objects.create(
            api_key=api_key,
            user=user,
            event_type=event_type,
            description=description,
            ip_address=ip_address,
            endpoint=endpoint,
            status_code=status_code,
            metadata=metadata or {},
        )