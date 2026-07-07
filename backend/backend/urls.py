from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from core.health import HealthCheckView, SecurityStatusView
import os
from core.metrics import inc_api_key_usage

def welcome_api(request):
    inc_api_key_usage("web", "/")
    return JsonResponse({
        "message": "Welcome to Vitmain Marketing API (Django)",
        "version": "1.0.0",
        "status": "running"
    })

urlpatterns = [
    
    # Welcome & Admin
    path('', welcome_api, name='welcome_api'),
    path('admin/', admin.site.urls),
    
    # Health checks
    path('health/', HealthCheckView.as_view(), name='health_check'),
    path('security-status/', SecurityStatusView.as_view(), name='security_status'),
    
    # API endpoints
    path('api/', include('users.urls')),
    path('api/', include('subscriptions.urls')),
    path('api/', include('onboarding.urls')),
    path('api/', include('chat.urls')),
    path('api/', include('support.urls')),
    path('api/portfolio/', include('portfolio.urls')),
    path('api/payments/', include('payments.urls', namespace='payments')),
    path('api/', include('core.urls')),
    path("", include("django_prometheus.urls")),
]

if os.environ.get("ENABLE_PROMETHEUS", "false").lower() == "true":
    urlpatterns += [
        path("", include("django_prometheus.urls")),
    ]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)