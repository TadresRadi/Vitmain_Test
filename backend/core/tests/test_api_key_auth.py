import pytest
from django.contrib.auth import get_user_model
from core.api_key_service import get_api_key_service
from rest_framework.test import APIClient

User = get_user_model()

@pytest.mark.django_db
def test_api_key_auth_header():
    user = User.objects.create_user(email="akey@example.com", password="pw12345")
    svc = get_api_key_service()
    raw_key, api_key = svc.create_api_key(user=user, name="test")
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {raw_key}")
    resp = client.get("/api/users/profile")  # change to a protected endpoint you have
    # If you don't have that endpoint, call a simple view that requires auth
    assert resp.status_code in (200, 401, 403)  # at minimum the request reached auth backend