from decimal import Decimal

import pytest

from payments.models import PaymentOrder


CREATE_ORDER_URL = "/api/payments/create-order/"


@pytest.mark.django_db
@pytest.mark.money
def test_create_payment_order_requires_auth(client, basic_plan):
    response = client.post(
        CREATE_ORDER_URL,
        {"plan": "basic", "expected_sender_number": "01012345678"},
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
@pytest.mark.money
def test_create_payment_order_validates_required_fields(auth_client):
    missing_number = auth_client.post(CREATE_ORDER_URL, {"plan": "basic"}, format="json")
    missing_plan = auth_client.post(
        CREATE_ORDER_URL,
        {"expected_sender_number": "01012345678"},
        format="json",
    )

    assert missing_number.status_code == 400
    assert missing_number.data["error"] == "expected_sender_number is required."
    assert missing_plan.status_code == 400
    assert missing_plan.data["error"] == "plan is required."


@pytest.mark.django_db
@pytest.mark.money
def test_create_payment_order_rejects_invalid_egyptian_mobile(auth_client, basic_plan):
    response = auth_client.post(
        CREATE_ORDER_URL,
        {"plan": "basic", "expected_sender_number": "01912345678"},
        format="json",
    )

    assert response.status_code == 400
    assert response.data["error"] == "Invalid Egyptian mobile number."


@pytest.mark.django_db
@pytest.mark.money
def test_create_payment_order_creates_backend_priced_order(auth_client, basic_plan, vodafone_settings):
    response = auth_client.post(
        CREATE_ORDER_URL,
        {"plan": "basic", "expected_sender_number": "010 1234 5678"},
        format="json",
    )

    assert response.status_code == 201
    user = auth_client.handler._force_user
    order = PaymentOrder.objects.get(user=user)
    assert order.expected_amount == basic_plan.price
    assert order.expected_sender_number == "01012345678"
    assert response.data["amount"] == Decimal("200.00")
    assert response.data["remaining_amount"] == Decimal("200.00")
    assert response.data["receiver_number"] == vodafone_settings.VODAFONE_RECEIVER_NUMBER


@pytest.mark.django_db
@pytest.mark.money
def test_create_payment_order_reuses_pending_order_and_updates_sender(auth_client, basic_plan):
    user = auth_client.handler._force_user
    order = PaymentOrder.objects.create(
        user=user,
        plan="basic",
        expected_amount=basic_plan.price,
        expected_sender_number="01011111111",
        reference_code="VFC123456",
    )

    response = auth_client.post(
        CREATE_ORDER_URL,
        {"plan": "basic", "expected_sender_number": "01122222222"},
        format="json",
    )

    assert response.status_code == 200
    assert PaymentOrder.objects.filter(user=user).count() == 1
    order.refresh_from_db()
    assert order.expected_sender_number == "01122222222"
    assert response.data["reference_code"] == "VFC123456"
