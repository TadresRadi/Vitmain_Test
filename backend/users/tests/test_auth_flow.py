import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
def test_login_refresh_logout():
    """Test the full auth flow with httpOnly cookie refresh tokens.

    Flow:
    1. Login → access in JSON, refresh in httpOnly cookie
    2. Refresh → reads cookie, returns new access, sets new refresh cookie
    3. Old refresh is blacklisted (rotation)
    4. Logout → clears cookie, blacklists current refresh
    """
    client = APIClient()
    user = User.objects.create_user(
        email="flow@example.com",
        password="testpass123",
    )

    # 1. Login — access token in body, refresh token in cookie
    resp = client.post(
        "/api/auth/login",
        {
            "email": user.email,
            "password": "testpass123",
        },
        format="json",
    )
    assert resp.status_code == 200, f"Login failed: {resp.data}"

    access = resp.data.get("access") or resp.data.get("access_token")
    assert access, "Login response missing access token"

    # Refresh token should NOT be in the response body (security)
    assert "refresh" not in resp.data, "Refresh token leaked in response body!"
    assert "refresh_token" not in resp.data, "Refresh token leaked in response body!"

    # Refresh token should be in the cookie
    assert "vitmain_refresh" in resp.cookies, "Refresh cookie not set!"

    # 2. Refresh — cookie is sent automatically by APIClient
    # No body needed — the view reads from the cookie
    r = client.post("/api/auth/refresh", {}, format="json")
    assert r.status_code == 200, f"Token refresh failed: {r.data}"
    assert "access" in r.data, "Refresh response missing access token"

    # 3. Logout — blacklists refresh token and clears cookie
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")
    rr = client.post("/api/auth/logout", {}, format="json")
    assert rr.status_code == 200, f"Logout failed: {rr.data}"
    assert "message" in rr.data, "Logout response missing 'message' field"

    # 4. After logout, refresh should fail (cookie cleared or blacklisted)
    r2 = client.post("/api/auth/refresh", {}, format="json")
    assert r2.status_code == 401, \
        f"Refresh should fail after logout, got {r2.status_code}"