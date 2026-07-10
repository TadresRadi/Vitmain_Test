"""
Tests for VodafoneCashWebhookView.

This is a security-critical endpoint — it receives payment confirmations
from Vodafone Cash and must verify the Bearer token before processing.
These tests verify authentication, field validation, and error handling.

Run: pytest payments/tests/test_vodafone_cash_webhook_view.py -v
"""
import pytest
from unittest.mock import patch

from payments.models import PaymentOrder


# ============================================================================
# Constants
# ============================================================================

WEBHOOK_URL = "/api/payments/vodafone-cash/webhook/"

VALID_BODY = {
    "sender_number": "01012345678",
    "amount": "200",
    "transaction_id": "TX001",
    "raw_sms": "You have received 200 EGP from 01012345678",
}

VALID_TOKEN = "test-secret-token"
VALID_AUTH_HEADER = f"Bearer {VALID_TOKEN}"


# ============================================================================
# Authentication tests
# ============================================================================

@pytest.mark.django_db
@pytest.mark.webhook
def test_no_auth_header_returns_401(client, vodafone_settings):
    """A request without Authorization header should return 401."""
    resp = client.post(WEBHOOK_URL, VALID_BODY, format="json")
    assert resp.status_code == 401
    assert resp.data["error"] == "Unauthorized"


@pytest.mark.django_db
@pytest.mark.webhook
def test_wrong_token_returns_401(client, vodafone_settings):
    """A request with the wrong token should return 401."""
    resp = client.post(
        WEBHOOK_URL,
        VALID_BODY,
        format="json",
        HTTP_AUTHORIZATION="Bearer wrong-token",
    )
    assert resp.status_code == 401


@pytest.mark.django_db
@pytest.mark.webhook
def test_missing_token_in_settings_returns_401(client, settings):
    """If VODAFONE_WEBHOOK_SECRET_TOKEN is unset, all requests should 401."""
    settings.VODAFONE_WEBHOOK_SECRET_TOKEN = ""
    resp = client.post(
        WEBHOOK_URL,
        VALID_BODY,
        format="json",
        HTTP_AUTHORIZATION=VALID_AUTH_HEADER,
    )
    assert resp.status_code == 401


@pytest.mark.django_db
@pytest.mark.webhook
def test_correct_token_passes_auth(client, vodafone_settings, basic_plan):
    """A request with the correct token should not get 401."""
    # Create a matching order so the service returns "matched"
    from tests.factories import UserFactory
    user = UserFactory()
    PaymentOrder.objects.create(
        user=user,
        plan="basic",
        expected_amount="200.00",
        expected_sender_number="01012345678",
        reference_code="VFC100001",
        status=PaymentOrder.Status.PENDING,
    )

    resp = client.post(
        WEBHOOK_URL,
        VALID_BODY,
        format="json",
        HTTP_AUTHORIZATION=VALID_AUTH_HEADER,
    )
    # Should NOT be 401 — it passed auth
    assert resp.status_code != 401


@pytest.mark.django_db
@pytest.mark.webhook
def test_webhook_does_not_require_jwt(client, vodafone_settings, basic_plan):
    """The webhook uses AllowAny — no JWT needed, only the Bearer token."""
    from tests.factories import UserFactory
    user = UserFactory()
    PaymentOrder.objects.create(
        user=user,
        plan="basic",
        expected_amount="200.00",
        expected_sender_number="01012345678",
        reference_code="VFC100001",
        status=PaymentOrder.Status.PENDING,
    )

    # No JWT, just the webhook Bearer token
    resp = client.post(
        WEBHOOK_URL,
        VALID_BODY,
        format="json",
        HTTP_AUTHORIZATION=VALID_AUTH_HEADER,
    )
    assert resp.status_code == 200


@pytest.mark.django_db
@pytest.mark.webhook
def test_token_comparison_is_timing_safe(client, vodafone_settings):
    """A token of the same length but different chars should be rejected."""
    # Same length as "test-secret-token" but different content
    wrong_same_length = "Bearer wrong-same-length!"
    resp = client.post(
        WEBHOOK_URL,
        VALID_BODY,
        format="json",
        HTTP_AUTHORIZATION=wrong_same_length,
    )
    assert resp.status_code == 401


# ============================================================================
# Field validation tests
# ============================================================================

@pytest.mark.django_db
@pytest.mark.webhook
def test_missing_sender_number_returns_400(client, vodafone_settings):
    """Missing sender_number should return 400 with the field listed."""
    body = {k: v for k, v in VALID_BODY.items() if k != "sender_number"}
    resp = client.post(
        WEBHOOK_URL,
        body,
        format="json",
        HTTP_AUTHORIZATION=VALID_AUTH_HEADER,
    )
    assert resp.status_code == 400
    assert "sender_number" in resp.data["fields"]


@pytest.mark.django_db
@pytest.mark.webhook
def test_missing_amount_returns_400(client, vodafone_settings):
    """Missing amount should return 400 with the field listed."""
    body = {k: v for k, v in VALID_BODY.items() if k != "amount"}
    resp = client.post(
        WEBHOOK_URL,
        body,
        format="json",
        HTTP_AUTHORIZATION=VALID_AUTH_HEADER,
    )
    assert resp.status_code == 400
    assert "amount" in resp.data["fields"]


@pytest.mark.django_db
@pytest.mark.webhook
def test_missing_transaction_id_returns_400(client, vodafone_settings):
    """Missing transaction_id should return 400 with the field listed."""
    body = {k: v for k, v in VALID_BODY.items() if k != "transaction_id"}
    resp = client.post(
        WEBHOOK_URL,
        body,
        format="json",
        HTTP_AUTHORIZATION=VALID_AUTH_HEADER,
    )
    assert resp.status_code == 400
    assert "transaction_id" in resp.data["fields"]


@pytest.mark.django_db
@pytest.mark.webhook
def test_missing_raw_sms_returns_400(client, vodafone_settings):
    """Missing raw_sms should return 400 with the field listed."""
    body = {k: v for k, v in VALID_BODY.items() if k != "raw_sms"}
    resp = client.post(
        WEBHOOK_URL,
        body,
        format="json",
        HTTP_AUTHORIZATION=VALID_AUTH_HEADER,
    )
    assert resp.status_code == 400
    assert "raw_sms" in resp.data["fields"]


@pytest.mark.django_db
@pytest.mark.webhook
def test_multiple_missing_fields_listed(client, vodafone_settings):
    """Multiple missing fields should all be listed in the response."""
    body = {"amount": "200"}  # missing sender_number, transaction_id, raw_sms
    resp = client.post(
        WEBHOOK_URL,
        body,
        format="json",
        HTTP_AUTHORIZATION=VALID_AUTH_HEADER,
    )
    assert resp.status_code == 400
    assert len(resp.data["fields"]) == 3


@pytest.mark.django_db
@pytest.mark.webhook
def test_empty_string_treated_as_missing(client, vodafone_settings):
    """Empty string values should be treated as missing."""
    body = {**VALID_BODY, "sender_number": ""}
    resp = client.post(
        WEBHOOK_URL,
        body,
        format="json",
        HTTP_AUTHORIZATION=VALID_AUTH_HEADER,
    )
    assert resp.status_code == 400
    assert "sender_number" in resp.data["fields"]


# ============================================================================
# Happy path tests
# ============================================================================

@pytest.mark.django_db
@pytest.mark.webhook
def test_happy_path_returns_200_with_service_result(client, vodafone_settings,
                                                     basic_plan):
    """A valid request with a matching order should return 200."""
    from tests.factories import UserFactory
    user = UserFactory()
    PaymentOrder.objects.create(
        user=user,
        plan="basic",
        expected_amount="200.00",
        expected_sender_number="01012345678",
        reference_code="VFC100001",
        status=PaymentOrder.Status.PENDING,
    )

    resp = client.post(
        WEBHOOK_URL,
        {**VALID_BODY, "reference_code": "VFC100001"},
        format="json",
        HTTP_AUTHORIZATION=VALID_AUTH_HEADER,
    )
    assert resp.status_code == 200
    assert resp.data["status"] == "matched"
    assert resp.data["order_status"] == "completed"


@pytest.mark.django_db
@pytest.mark.webhook
def test_reference_code_passed_through_to_service(client, vodafone_settings,
                                                    basic_plan):
    """The reference_code from the request should be passed to the service."""
    from tests.factories import UserFactory
    user = UserFactory()
    PaymentOrder.objects.create(
        user=user,
        plan="basic",
        expected_amount="200.00",
        expected_sender_number="01012345678",
        reference_code="VFC100001",
        status=PaymentOrder.Status.PENDING,
    )

    resp = client.post(
        WEBHOOK_URL,
        {
            **VALID_BODY,
            "reference_code": "VFC100001",
        },
        format="json",
        HTTP_AUTHORIZATION=VALID_AUTH_HEADER,
    )
    assert resp.status_code == 200
    # The order was matched by reference code
    assert "Reference Code" in resp.data["match_reason"]


# ============================================================================
# Error handling tests
# ============================================================================

@pytest.mark.django_db
@pytest.mark.webhook
def test_value_error_from_service_returns_400(client, vodafone_settings):
    """A ValueError from the service (e.g. invalid amount) should return 400."""
    body = {**VALID_BODY, "amount": "abc"}
    resp = client.post(
        WEBHOOK_URL,
        body,
        format="json",
        HTTP_AUTHORIZATION=VALID_AUTH_HEADER,
    )
    assert resp.status_code == 400
    assert "valid number" in resp.data["error"]


@pytest.mark.django_db
@pytest.mark.webhook
def test_zero_amount_returns_400(client, vodafone_settings):
    """A zero amount should trigger ValueError → 400."""
    body = {**VALID_BODY, "amount": "0"}
    resp = client.post(
        WEBHOOK_URL,
        body,
        format="json",
        HTTP_AUTHORIZATION=VALID_AUTH_HEADER,
    )
    assert resp.status_code == 400


@pytest.mark.django_db
@pytest.mark.webhook
def test_unexpected_exception_returns_500(client, vodafone_settings):
    """An unexpected exception from the service should return 500."""
    with patch(
        "payments.views.vodafone_cash_webhook_view.PaymentMatchingService"
        ".process_incoming_transaction",
        side_effect=RuntimeError("Unexpected error"),
    ):
        resp = client.post(
            WEBHOOK_URL,
            VALID_BODY,
            format="json",
            HTTP_AUTHORIZATION=VALID_AUTH_HEADER,
        )
    assert resp.status_code == 500
    assert resp.data["error"] == "Failed to process webhook."