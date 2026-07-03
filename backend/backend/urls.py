from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static

def welcome_api(request):
    return JsonResponse({"message": "Welcome to Vitmain Marketing API (Django)"})

urlpatterns = [
    # Welcome & Admin
    path('', welcome_api, name='welcome_api'),
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/', include('users.urls')),
    path('api/', include('subscriptions.urls')),
    path('api/', include('onboarding.urls')),
    path('api/', include('chat.urls')),
    path('api/', include('support.urls')),
    path('api/portfolio/', include('portfolio.urls')),
    path('api/payments/', include('payments.urls', namespace='payments')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
