"""
Tests for SubscriptionStatusView.

Endpoint: GET /api/subscription/status

Run: pytest subscriptions/tests/test_subscription_status_view.py -v
"""
import pytest



STATUS_URL = "/api/subscription/status"


@pytest.mark.django_db
def test_unauthenticated_returns_401(client):
    """Unauthenticated requests should return 401."""
    resp = client.get(STATUS_URL)
    assert resp.status_code == 401


@pytest.mark.django_db
def test_no_subscription_returns_active_false(auth_client):
    """A user with no subscription should get {"active": false}."""
    resp = auth_client.get(STATUS_URL)
    assert resp.status_code == 200
    assert resp.data == {"active": False}


@pytest.mark.django_db
def test_existing_subscription_returned(auth_client, basic_plan):
    """A user with a subscription should get the serialized subscription."""
    from tests.factories import SubscriptionFactory
    user = auth_client.handler._force_user
    SubscriptionFactory(user=user, plan=basic_plan, active=True)

    resp = auth_client.get(STATUS_URL)
    assert resp.status_code == 200

    # Should have subscription fields, not {"active": false}
    assert "id" in resp.data
    assert "plan" in resp.data
    assert resp.data["active"] is True
    assert resp.data["plan"]["slug"] == "basic"