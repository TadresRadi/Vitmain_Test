"""
Core app URLs.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views.api_key_views import APIKeyViewSet
from core.health import HealthCheckView, SecurityStatusView

router = DefaultRouter()
router.register(r'api-keys', APIKeyViewSet, basename='api-key')

urlpatterns = [
    path('', include(router.urls)),
    path('health/', HealthCheckView.as_view(), name='health'),
    path('health/security', SecurityStatusView.as_view(), name='security_status'),
]