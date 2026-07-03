from django.urls import path
from django.http import JsonResponse
from onboarding.views.onboarding_response_view import OnboardingResponseView

def test_onboarding(request):
    return JsonResponse({"message": "Onboarding app is working"})

urlpatterns = [
    path('test/', test_onboarding, name='test_onboarding'),
    path('onboarding/', OnboardingResponseView.as_view(), name='user_onboarding'),
]
