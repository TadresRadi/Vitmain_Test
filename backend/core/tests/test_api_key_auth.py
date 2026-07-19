import pytest
from django.contrib.auth import get_user_model
from core.api_key_service import get_api_key_service
from rest_framework.test import APIClient

User = get_user_model()

# Shared dummy password for API-key auth tests. Not a real credential.
TEST_PASSWORD = "pw12345"  # nosec B105 - test fixture, not a real credential


@pytest.mark.django_db
def test_api_key_auth_header():
    """A valid API key in the Authorization header should authenticate the request."""
    user = User.objects.create_user(
        email="akey@example.com",
        password=TEST_PASSWORD,
    )
    svc = get_api_key_service()
    raw_key, _api_key = svc.create_api_key(user=user, name="test")

    # Authenticate with the raw API key
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {raw_key}")

    # /api/users/profile requires IsAuthenticated — a valid API key
    # should grant access and return 200.
    resp = client.get("/api/users/profile")

    assert resp.status_code == 200, (
        f"API key auth failed: expected 200, got {resp.status_code}. "
        f"Response: {resp.data}"
    )


@pytest.mark.django_db
def test_api_key_auth_rejected_with_invalid_key():
    """An invalid API key should be rejected with 401."""
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Bearer vitmain_invalid_key_that_does_not_exist")

    resp = client.get("/api/users/profile")

    assert resp.status_code == 401, (
        f"Invalid API key should be rejected: expected 401, got {resp.status_code}. "
        f"Response: {resp.data}"
    )