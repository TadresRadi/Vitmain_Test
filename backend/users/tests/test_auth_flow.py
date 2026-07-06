import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

@pytest.mark.django_db
def test_login_refresh_logout():
    client = APIClient()
    user = User.objects.create_user(email="flow@example.com", password="testpass123")
    # login (assumes token endpoint at /auth/login)
    resp =  client.post(
    "/api/auth/login",
    {
        "email": user.email,
        "password": "testpass123"
    },
    format="json"
)
    # adjust path above to your MyTokenObtainPairView path; if you use /auth/login as in users/urls.py use that.
    assert resp.status_code in (200, 201)
    access = resp.data.get("access")
    refresh = resp.data.get("refresh")
    assert access
    assert refresh
    # refresh
    r = client.post("/api/auth/refresh", {"refresh": refresh}, format='json')
    assert r.status_code == 200
    # logout -> blacklist refresh (assuming your LogoutView at /auth/logout)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    rr = client.post("/api/auth/logout", {"refresh_token": refresh}, format='json')
    assert rr.status_code in (200, 204, 202)
    # confirm refresh cannot be used (should raise invalid)
    r2 = client.post("/api/auth/refresh", {"refresh": refresh}, format='json')
    assert r2.status_code != 200