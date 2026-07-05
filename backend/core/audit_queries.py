"""
Helper queries for audit logs.
For reporting and monitoring.
"""
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from core.models import AuditLog


class AuditLogQueries:
    """Helper class for common audit log queries."""
    
    @staticmethod
    def get_failed_logins(hours: int = 24) -> int:
        """
        Get count of failed login attempts in last N hours.
        
        Args:
            hours: Number of hours to look back
        
        Returns:
            Count of failed logins
        """
        since = timezone.now() - timedelta(hours=hours)
        return AuditLog.objects.filter(
            action='login_failure',
            created_at__gte=since,
        ).count()
    
    @staticmethod
    def get_user_activity_timeline(user_email: str, days: int = 30):
        """
        Get user's activity timeline.
        
        Args:
            user_email: User email
            days: Number of days to look back
        
        Returns:
            QuerySet of audit logs
        """
        since = timezone.now() - timedelta(days=days)
        return AuditLog.objects.filter(
            user__email=user_email,
            created_at__gte=since,
        ).order_by('-created_at')
    
    @staticmethod
    def get_suspicious_ips(hours: int = 24, threshold: int = 10):
        """
        Get IPs with many failed attempts.
        
        Args:
            hours: Number of hours to look back
            threshold: Minimum number of failed attempts
        
        Returns:
            List of suspicious IPs with counts
        """
        since = timezone.now() - timedelta(hours=hours)
        return (
            AuditLog.objects
            .filter(
                action='login_failure',
                created_at__gte=since,
                details__user_ip__isnull=False,
            )
            .values('details__user_ip')
            .annotate(count=Count('id'))
            .filter(count__gte=threshold)
            .order_by('-count')
        )
    
    @staticmethod
    def get_critical_events(hours: int = 24):
        """
        Get all critical security events.
        
        Args:
            hours: Number of hours to look back
        
        Returns:
            QuerySet of critical events
        """
        since = timezone.now() - timedelta(hours=hours)
        return AuditLog.objects.filter(
            details__severity='critical',
            created_at__gte=since,
        ).order_by('-created_at')
    
    @staticmethod
    def get_unauthorized_access_attempts(hours: int = 24):
        """
        Get all unauthorized access attempts.
        
        Args:
            hours: Number of hours to look back
        
        Returns:
            QuerySet of unauthorized attempts
        """
        since = timezone.now() - timedelta(hours=hours)
        return AuditLog.objects.filter(
            action='permission_denied',
            created_at__gte=since,
        ).order_by('-created_at')
    
    @staticmethod
    def get_rate_limit_violations(hours: int = 24):
        """
        Get all rate limit violations.
        
        Args:
            hours: Number of hours to look back
        
        Returns:
            QuerySet of rate limit violations
        """
        since = timezone.now() - timedelta(hours=hours)
        return AuditLog.objects.filter(
            action='rate_limit_exceeded',
            created_at__gte=since,
        ).select_related('user').order_by('-created_at')
