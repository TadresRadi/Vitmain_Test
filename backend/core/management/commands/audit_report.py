"""
Management command for generating audit reports.
"""
from django.core.management.base import BaseCommand
from core.audit_queries import AuditLogQueries


class Command(BaseCommand):
    help = 'Generate audit report'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Hours to look back (default: 24)',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='User email for activity report',
        )

    def handle(self, *args, **options):
        hours = options['hours']
        email = options['email']

        self.stdout.write(self.style.SUCCESS('=== Audit Report ==='))
        self.stdout.write(f'Period: Last {hours} hours\n')

        if email:
            self.stdout.write(f'User: {email}\n')
            self._user_report(email, hours)
        else:
            self._security_report(hours)

    def _security_report(self, hours: int):
        """Generate security report."""
        self.stdout.write('\n--- Security Events ---')
        
        # Failed logins
        failed_logins = AuditLogQueries.get_failed_logins(hours)
        self.stdout.write(f'Failed login attempts: {failed_logins}')
        
        # Critical events
        critical_events = AuditLogQueries.get_critical_events(hours)
        self.stdout.write(f'Critical events: {critical_events.count()}')
        
        # Unauthorized access
        unauthorized = AuditLogQueries.get_unauthorized_access_attempts(hours)
        self.stdout.write(f'Unauthorized access attempts: {unauthorized.count()}')
        
        # Rate limit violations
        rate_limits = AuditLogQueries.get_rate_limit_violations(hours)
        self.stdout.write(f'Rate limit violations: {rate_limits.count()}')
        
        # Suspicious IPs
        self.stdout.write('\n--- Suspicious IPs ---')
        suspicious_ips = AuditLogQueries.get_suspicious_ips(hours)
        for ip_data in suspicious_ips[:10]:
            self.stdout.write(
                f"  {ip_data['details__user_ip']}: {ip_data['count']} attempts"
            )

    def _user_report(self, email: str, hours: int):
        """Generate user activity report."""
        self.stdout.write('\n--- User Activity ---')
        
        timeline = AuditLogQueries.get_user_activity_timeline(email, days=1)
        
        for log in timeline[:20]:
            self.stdout.write(
                f"  {log.created_at.strftime('%H:%M:%S')} - "
                f"{log.action} - {log.details.get('severity', 'info')}"
            )
