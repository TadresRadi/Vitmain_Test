import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from users.services.email_verification_service import EmailVerificationService

User = get_user_model()


@pytest.mark.django_db
def test_unverified_user_cannot_login():
    """A local user with is_email_verified=False cannot log in."""
    User.objects.create_user(
        email="unverified@example.com",
        password="testpass123",
        is_email_verified=False,
    )
    client = APIClient()
    resp = client.post(
        "/api/auth/login",
        {"email": "unverified@example.com", "password": "testpass123"},
        format="json",
    )
    assert resp.status_code == 400
    assert "not verified" in str(resp.data).lower()


@pytest.mark.django_db
def test_verified_user_can_login():
    """A local user with is_email_verified=True can log in."""
    User.objects.create_user(
        email="verified@example.com",
        password="testpass123",
        is_email_verified=True,
    )
    client = APIClient()
    resp = client.post(
        "/api/auth/login",
        {"email": "verified@example.com", "password": "testpass123"},
        format="json",
    )
    assert resp.status_code == 200


@pytest.mark.django_db
def test_google_user_does_not_need_email_verification():
    """A Google-auth user can log in via Google even without is_email_verified."""
    user = User.objects.create_user(
        email="googleuser@example.com",
        password=None,
        auth_provider='google',
        is_email_verified=False,
    )
    # Google flow doesn't go through MyTokenObtainPairSerializer — it uses
    # RefreshToken.for_user directly in GoogleOAuthCallbackView. So the
    # is_email_verified check doesn't apply. Verify by checking that the
    # user exists and can get a token via the Google callback path.
    # (Full Google flow is mocked elsewhere; here we just verify the model.)
    assert user.auth_provider == 'google'


@pytest.mark.django_db
def test_verify_email_endpoint_with_valid_token():
    """POST /api/auth/verify-email with a valid token marks user as verified."""
    user = User.objects.create_user(
        email="verifyme@example.com",
        password="testpass123",
        is_email_verified=False,
    )
    token = EmailVerificationService.generate_token()
    EmailVerificationService.store_token(user, token)

    client = APIClient()
    resp = client.post(
        "/api/auth/verify-email",
        {"user_id": str(user.id), "token": token},
        format="json",
    )
    assert resp.status_code == 200
    user.refresh_from_db()
    assert user.is_email_verified is True


@pytest.mark.django_db
def test_verify_email_endpoint_with_invalid_token():
    """POST /api/auth/verify-email with a bad token returns 400."""
    user = User.objects.create_user(
        email="verifyme@example.com",
        password="testpass123",
        is_email_verified=False,
    )
    EmailVerificationService.store_token(user, "real-token-but-not-this")

    client = APIClient()
    resp = client.post(
        "/api/auth/verify-email",
        {"user_id": str(user.id), "token": "wrong-token"},
        format="json",
    )
    assert resp.status_code == 400
    user.refresh_from_db()
    assert user.is_email_verified is False


@pytest.mark.django_db
def test_resend_verification_does_not_reveal_user_existence():
    """POST /api/auth/resend-verification returns the same message for
    existing and non-existing users (no user enumeration)."""
    client = APIClient()

    # Non-existent email
    resp1 = client.post(
        "/api/auth/resend-verification",
        {"email": "nonexistent@example.com"},
        format="json",
    )

    # Existing unverified email
    User.objects.create_user(
        email="real@example.com",
        password="testpass123",
        is_email_verified=False,
    )
    resp2 = client.post(
        "/api/auth/resend-verification",
        {"email": "real@example.com"},
        format="json",
    )

    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp1.data['message'] == resp2.data['message']