"""
Shared pytest fixtures and configuration.

Fixtures defined here are available to all test files without importing.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from tests.factories import UserFactory, PlanFactory

User = get_user_model()


# ============================================================================
# Core fixtures
# ============================================================================

@pytest.fixture
def user(db):
    """Standard authenticated user."""
    return UserFactory()


@pytest.fixture
def admin_user(db):
    """Super admin user."""
    return UserFactory(role="super_admin", is_staff=True, is_superuser=True)


@pytest.fixture
def api_client():
    """DRF APIClient without authentication."""
    return APIClient()


@pytest.fixture
def auth_client(api_client, user):
    """API client authenticated as `user` via JWT.

    Uses force_authenticate so that request.user is set without
    going through the actual JWT middleware. The `user` instance
    is accessible via `auth_client.handler._force_user`.
    """
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def admin_client(api_client, admin_user):
    """API client authenticated as an admin user."""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def rf():
    """RequestFactory for building raw requests."""
    return RequestFactory()


@pytest.fixture
def anon_request(rf):
    """Anonymous request (no authenticated user)."""
    req = rf.get("/")
    req.user = AnonymousUser()
    return req


# ============================================================================
# Plan fixtures
# ============================================================================

@pytest.fixture
def basic_plan(db):
    """The 'basic' plan (chat/AI campaign generation — 200 EGP)."""
    from decimal import Decimal
    return PlanFactory(
        name="Basic",
        slug="basic",
        price=Decimal("200.00"),
    )


@pytest.fixture
def pro_plan(db):
    """The 'pro' plan (support/premium — 500 EGP)."""
    from decimal import Decimal
    return PlanFactory(
        name="Pro",
        slug="pro",
        price=Decimal("500.00"),
    )


# ============================================================================
# Settings overrides
# ============================================================================

@pytest.fixture
def vodafone_settings(settings):
    """
    Override Vodafone webhook config for tests.

    Ensures the webhook has a known token and receiver number without
    requiring real environment variables.
    """
    settings.VODAFONE_RECEIVER_NUMBER = "01098765432"
    settings.VODAFONE_WEBHOOK_SECRET_TOKEN = "test-secret-token"
    return settings