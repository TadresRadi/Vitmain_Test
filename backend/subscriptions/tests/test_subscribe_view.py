"""
Tests for SubscribeView.

Verifies plan routing: basic plan redirects to payment, pro plan
activates subscription immediately, unknown plans return 400.

Endpoint: POST /api/subscription/subscribe

Run: pytest subscriptions/tests/test_subscribe_view.py -v
"""
import pytest
from decimal import Decimal

from subscriptions.models import Subscription
from core.models import AuditLog


SUBSCRIBE_URL = "/api/subscription/subscribe"


# ============================================================================
# Auth tests
# ============================================================================

@pytest.mark.django_db
def test_unauthenticated_returns_401(client):
    """Unauthenticated requests should return 401."""
    resp = client.post(SUBSCRIBE_URL, {"plan_slug": "basic"}, format="json")
    assert resp.status_code == 401


# ============================================================================
# Input validation
# ============================================================================

@pytest.mark.django_db
def test_missing_plan_slug_returns_400(auth_client):
    """Missing plan_slug should return 400."""
    resp = auth_client.post(SUBSCRIBE_URL, {}, format="json")
    assert resp.status_code == 400
    assert "plan_slug" in resp.data["error"]


@pytest.mark.django_db
def test_unknown_plan_slug_returns_404(auth_client):
    """A plan_slug that doesn't exist in the DB should return 404."""
    resp = auth_client.post(
        SUBSCRIBE_URL,
        {"plan_slug": "nonexistent-plan"},
        format="json",
    )
    assert resp.status_code == 404
    assert "not found" in resp.data["error"].lower()


# ============================================================================
# Basic plan (chat) — redirects to payment
# ============================================================================

@pytest.mark.django_db
def test_basic_plan_returns_redirect_payment(auth_client, basic_plan):
    """The basic plan should return redirect_payment, not auto-activate."""
    resp = auth_client.post(
        SUBSCRIBE_URL,
        {"plan_slug": "basic"},
        format="json",
    )
    assert resp.status_code == 200
    assert resp.data["action"] == "redirect_payment"
    assert resp.data["plan_slug"] == "basic"
    assert resp.data["amount"] == float(basic_plan.price)

    # No subscription should be created — payment must complete first
    user = auth_client.handler._force_user
    assert not Subscription.objects.filter(user=user).exists()


# ============================================================================
# Pro plan (support) — activates immediately
# ============================================================================

@pytest.mark.django_db
def test_pro_plan_returns_redirect_support(auth_client, pro_plan):
    """The pro plan should activate the subscription and return redirect_support."""
    resp = auth_client.post(
        SUBSCRIBE_URL,
        {"plan_slug": "pro"},
        format="json",
    )
    assert resp.status_code == 200
    assert resp.data["action"] == "redirect_support"
    assert "subscription" in resp.data

    # Subscription should be created and active
    user = auth_client.handler._force_user
    sub = Subscription.objects.get(user=user)
    assert sub.active is True
    assert sub.plan.slug == "pro"


@pytest.mark.django_db
def test_pro_plan_updates_existing_subscription(auth_client, basic_plan, pro_plan):
    """Subscribing to pro should update, not duplicate, an existing subscription."""
    user = auth_client.handler._force_user

    # Create an existing basic subscription
    from tests.factories import SubscriptionFactory
    SubscriptionFactory(user=user, plan=basic_plan, active=True)

    # Subscribe to pro
    resp = auth_client.post(
        SUBSCRIBE_URL,
        {"plan_slug": "pro"},
        format="json",
    )
    assert resp.status_code == 200

    # Should still be only one subscription, now with pro plan
    assert Subscription.objects.filter(user=user).count() == 1
    sub = Subscription.objects.get(user=user)
    assert sub.plan.slug == "pro"
    assert sub.active is True


# ============================================================================
# Unknown plan (exists in DB but not basic/pro)
# ============================================================================

@pytest.mark.django_db
def test_unknown_plan_slug_after_plan_exists_returns_400(auth_client):
    """A plan that exists in DB but isn't basic or pro should return 400."""
    from tests.factories import PlanFactory
    PlanFactory(slug="enterprise", price=Decimal("1000.00"))

    resp = auth_client.post(
        SUBSCRIBE_URL,
        {"plan_slug": "enterprise"},
        format="json",
    )
    assert resp.status_code == 400
    assert "Unknown plan" in resp.data["error"]


# ============================================================================
# Audit logging
# ============================================================================

@pytest.mark.django_db
def test_pro_subscribe_logs_user_activity(auth_client, pro_plan):
    """Subscribing to pro should create an audit log entry."""
    user = auth_client.handler._force_user

    auth_client.post(SUBSCRIBE_URL, {"plan_slug": "pro"}, format="json")

    assert AuditLog.objects.filter(
        user=user,
        action="subscription_activated",
    ).exists()