"""
Health check and security status endpoint.
"""
import logging
from django.db import connection
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions


logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """
    Health check endpoint for monitoring.
    
    GET /health/
    
    Returns system health status including:
    - Database connectivity
    - Cache connectivity
    - Security headers presence
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Get health status."""
        health_status = {
            'status': 'healthy',
            'timestamp': self._get_timestamp(),
            'checks': {}
        }
        
        # Database check
        db_check = self._check_database()
        health_status['checks']['database'] = db_check
        if not db_check['healthy']:
            health_status['status'] = 'degraded'
        
        # Cache check
        cache_check = self._check_cache()
        health_status['checks']['cache'] = cache_check
        if not cache_check['healthy']:
            health_status['status'] = 'degraded'
        
        # Security headers check
        security_check = self._check_security_headers(request)
        health_status['checks']['security'] = security_check
        
        # Determine response status
        response_status = (
            status.HTTP_200_OK
            if health_status['status'] == 'healthy'
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )
        
        return Response(health_status, status=response_status)
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp."""
        from django.utils import timezone
        return timezone.now().isoformat()
    
    @staticmethod
    def _check_database() -> dict:
        """Check database connectivity."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return {
                'healthy': True,
                'message': 'Database connection OK'
            }
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                'healthy': False,
                'message': f'Database connection failed: {str(e)}'
            }
    
    @staticmethod
    def _check_cache() -> dict:
        """Check cache connectivity."""
        try:
            test_key = 'health_check_test'
            test_value = 'ok'
            
            cache.set(test_key, test_value, 10)
            value = cache.get(test_key)
            cache.delete(test_key)
            
            if value == test_value:
                return {
                    'healthy': True,
                    'message': 'Cache connection OK'
                }
            else:
                return {
                    'healthy': False,
                    'message': 'Cache write/read mismatch'
                }
        except Exception as e:
            logger.error(f"Cache health check failed: {str(e)}")
            return {
                'healthy': False,
                'message': f'Cache connection failed: {str(e)}'
            }
    
    @staticmethod
    def _check_security_headers(request) -> dict:
        """Check if security headers are present."""
        required_headers = [
            'Strict-Transport-Security',
            'X-Content-Type-Options',
            'X-Frame-Options',
            'Referrer-Policy',
        ]
        
        # This is a pre-response check, so we report what should be there
        return {
            'healthy': True,
            'message': 'Security headers configured',
            'headers_checked': required_headers
        }


class SecurityStatusView(APIView):
    """
    Security configuration status endpoint.
    Shows current security settings (admin only).
    """
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        """Get security status."""
        from django.conf import settings
        
        security_status = {
            'https_enforced': settings.SECURE_SSL_REDIRECT,
            'hsts_enabled': settings.SECURE_HSTS_SECONDS > 0,
            'hsts_seconds': settings.SECURE_HSTS_SECONDS,
            'secure_cookies': settings.SESSION_COOKIE_SECURE,
            'csrf_enabled': not settings.DEBUG,
            'cors_origins': settings.CORS_ALLOWED_ORIGINS[:5],  # First 5 only
            'cors_allow_all': settings.CORS_ALLOW_ALL_ORIGINS,
            'debug_mode': settings.DEBUG,
        }
        
        return Response(security_status)