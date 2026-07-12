"""
Admin configuration for core models.
"""

from django.contrib import admin
from django.utils.html import format_html
from core.models import AuditLog
from core.api_key_models import APIKey, APIKeyAuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin interface for audit logs."""

    list_display = (
        "created_at",
        "user",
        "action",
    )

    list_filter = (
        "action",
        "created_at",
    )

    search_fields = (
        "user__email",
        "action",
    )

    readonly_fields = (
        "id",
        "user",
        "action",
        "details",
        "created_at",
    )

    ordering = ("-created_at",)

    fieldsets = (
        (
            "Audit Log",
            {
                "fields": (
                    "id",
                    "user",
                    "action",
                    "details",
                    "created_at",
                )
            },
        ),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    
@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    """Admin interface for API keys."""
    
    list_display = [
        'name',
        'user',
        'key_prefix',
        'scope',
        'status_badge',
        'created_at',
        'last_used_at',
    ]
    
    list_filter = [
        'scope',
        'status',
        'created_at',
    ]
    
    search_fields = [
        'name',
        'user__email',
        'key_prefix',
    ]
    
    readonly_fields = [
        'key_prefix',
        'key_hash',
        'created_at',
        'updated_at',
        'last_used_at',
        'rotated_at',
    ]
    
    fieldsets = (
        ('Key Info', {
            'fields': (
                'name',
                'key_prefix',
                'scope',
                'status',
            )
        }),
        ('User', {
            'fields': ('user',)
        }),
        ('Expiry', {
            'fields': ('expires_at',)
        }),
        ('Restrictions', {
            'fields': ('allowed_ips',)
        }),
        ('Usage', {
            'fields': (
                'last_used_at',
                'last_ip',
            )
        }),
        ('Details', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
                'rotated_at',
            )
        }),
    )
    
    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'active': 'green',
            'inactive': 'gray',
            'revoked': 'red',
            'expired': 'orange',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion (use revoke instead)."""
        return False


@admin.register(APIKeyAuditLog)
class APIKeyAuditLogAdmin(admin.ModelAdmin):
    """Admin interface for API key audit logs."""
    
    list_display = [
        'created_at',
        'event_type',
        'api_key',
        'user',
        'ip_address',
    ]
    
    list_filter = [
        'event_type',
        'created_at',
    ]
    
    search_fields = [
        'api_key__name',
        'user__email',
        'ip_address',
    ]
    
    readonly_fields = [
        'api_key',
        'user',
        'event_type',
        'created_at',
        'metadata',
    ]
    
    def has_add_permission(self, request):
        """Prevent manual creation."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent editing."""
        return False