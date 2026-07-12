"""
Tests for PlanListView.

Endpoint: GET /api/plans

Run: pytest subscriptions/tests/test_plan_list_view.py -v
"""
import pytest
from decimal import Decimal



PLANS_URL = "/api/plans"


@pytest.mark.django_db
def test_list_plans_no_auth_required(client):
    """PlanListView uses AllowAny — no authentication needed."""
    resp = client.get(PLANS_URL)
    assert resp.status_code == 200


@pytest.mark.django_db
def test_returns_all_plans(client):
    """All plans in the database should be returned."""
    from tests.factories import PlanFactory
    PlanFactory(name="Basic", slug="basic", price=Decimal("200.00"))
    PlanFactory(name="Pro", slug="pro", price=Decimal("500.00"))
    PlanFactory(name="Enterprise", slug="enterprise", price=Decimal("1000.00"))

    resp = client.get(PLANS_URL)
    assert resp.status_code == 200
    # DRF pagination wraps results in {count, next, previous, results}
    assert resp.data["count"] == 3
    assert len(resp.data["results"]) == 3


@pytest.mark.django_db
def test_plan_serializer_fields(client, basic_plan):
    """Each plan should have the expected serializer fields."""
    resp = client.get(PLANS_URL)
    assert resp.status_code == 200

    plan = resp.data["results"][0]
    expected_fields = {"id", "name", "slug", "price", "description", "features"}
    assert set(plan.keys()) == expected_fields