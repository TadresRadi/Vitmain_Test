import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
def test_login_refresh_logout():
    """Test the full auth flow: login → refresh → logout."""
    client = APIClient()
    user = User.objects.create_user(
        email="flow@example.com",
        password="testpass123",
    )

    # 1. Login
    resp = client.post(
        "/api/auth/login",
        {
            "email": user.email,
            "password": "testpass123",
        },
        format="json",
    )
    assert resp.status_code == 200, f"Login failed: {resp.data}"

    access = resp.data.get("access")
    refresh = resp.data.get("refresh")
    assert access, "Login response missing access token"
    assert refresh, "Login response missing refresh token"

    # 2. Refresh
    r = client.post(
        "/api/auth/refresh",
        {"refresh": refresh},
        format="json",
    )
    assert r.status_code == 200, f"Token refresh failed: {r.data}"

    # 3. Logout — blacklist both access and refresh tokens
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    rr = client.post(
        "/api/auth/logout",
        {"refresh_token": refresh},
        format="json",
    )
    assert rr.status_code == 200, f"Logout failed: {rr.data}"
    assert "message" in rr.data, "Logout response missing 'message' field"