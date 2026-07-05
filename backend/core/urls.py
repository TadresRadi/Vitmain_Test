"""
Core app URLs.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views.api_key_views import APIKeyViewSet

router = DefaultRouter()
router.register(r'api-keys', APIKeyViewSet, basename='api-key')

urlpatterns = [
    path('', include(router.urls)),
]