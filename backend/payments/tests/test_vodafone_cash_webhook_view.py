"""
Tests for Vodafone Cash webhook view.

The webhook authenticates by HMAC-SHA256 signature over the raw request
body, computed using VODAFONE_WEBHOOK_SECRET_TOKEN.
"""
import hashlib
import hmac
import json

import pytest
from django.test import override_settings
from rest_framework.test import APIClient

WEBHOOK_SECRET = "test-webhook-secret-do-not-use-in-prod"
WEBHOOK_URL = "/api/payments/vodafone-cash/webhook/"


def sign(body: dict, secret: str = WEBHOOK_SECRET) -> str:
    """Compute the HMAC-SHA256 signature for a JSON body."""
    raw = json.dumps(body, separators=(",", ":")).encode("utf-8")
    return hmac.new(secret.encode("utf-8"), raw, hashlib.sha256).hexdigest()


def valid_payload(**overrides) -> dict:
    payload = {
        "sender_number": "01012345678",
        "amount": "200.00",
        "transaction_id": "TX-001",
        "raw_sms": "Received 200 EGP from 01012345678",
    }
    payload.update(overrides)
    return payload


@pytest.fixture
def webhook_client():
    return APIClient()


@pytest.fixture
def configured_secret(settings):
    settings.VODAFONE_WEBHOOK_SECRET_TOKEN = WEBHOOK_SECRET
    return settings


@pytest.mark.django_db
class TestVodafoneWebhookAuth:
    """Authentication / signature verification tests."""

    def test_rejects_request_without_signature(self, webhook_client, configured_secret):
        resp = webhook_client.post(
            WEBHOOK_URL,
            data=valid_payload(),
            format="json",
        )
        assert resp.status_code == 401

    def test_rejects_request_with_wrong_signature(self, webhook_client, configured_secret):
        payload = valid_payload()
        resp = webhook_client.post(
            WEBHOOK_URL,
            data=payload,
            format="json",
            HTTP_X_VODAFONE_SIGNATURE="deadbeef" * 8,
        )
        assert resp.status_code == 401

    def test_rejects_request_with_empty_signature(self, webhook_client, configured_secret):
        resp = webhook_client.post(
            WEBHOOK_URL,
            data=valid_payload(),
            format="json",
            HTTP_X_VODAFONE_SIGNATURE="",
        )
        assert resp.status_code == 401

    def test_rejects_request_when_secret_not_configured(self, webhook_client, settings):
        # Force the secret to be empty for this test
        settings.VODAFONE_WEBHOOK_SECRET_TOKEN = ""
        # The settings validator normally blocks boot when DEBUG=False and
        # the secret is missing. Here we just want to confirm the view
        # returns 500 (or 401 — either is acceptable).
        payload = valid_payload()
        sig = sign(payload, secret="some-other-secret")
        resp = webhook_client.post(
            WEBHOOK_URL,
            data=payload,
            format="json",
            HTTP_X_VODAFONE_SIGNATURE=sig,
        )
        # The view checks `if not configured_secret` and returns 500.
        assert resp.status_code == 500


@pytest.mark.django_db
class TestVodafoneWebhookPayload:
    """Payload validation tests (with valid signature)."""

    def test_rejects_missing_required_fields(self, webhook_client, configured_secret):
        payload = valid_payload()
        del payload["raw_sms"]
        resp = webhook_client.post(
            WEBHOOK_URL,
            data=payload,
            format="json",
            HTTP_X_VODAFONE_SIGNATURE=sign(payload),
        )
        assert resp.status_code == 400
        assert "raw_sms" in resp.data["fields"]

    def test_rejects_empty_required_fields(self, webhook_client, configured_secret):
        payload = valid_payload(sender_number="")
        resp = webhook_client.post(
            WEBHOOK_URL,
            data=payload,
            format="json",
            HTTP_X_VODAFONE_SIGNATURE=sign(payload),
        )
        assert resp.status_code == 400
        assert "sender_number" in resp.data["fields"]

    def test_rejects_empty_body(self, webhook_client, configured_secret):
        # Sign an empty body — view should reject before processing
        empty_sig = hmac.new(
            WEBHOOK_SECRET.encode("utf-8"),
            b"",
            hashlib.sha256,
        ).hexdigest()
        resp = webhook_client.post(
            WEBHOOK_URL,
            data="",
            content_type="application/json",
            HTTP_X_VODAFONE_SIGNATURE=empty_sig,
        )
        assert resp.status_code == 400


@pytest.mark.django_db
class TestVodafoneWebhookProcessing:
    """End-to-end webhook processing tests (with valid signature)."""

    def test_unmatched_transaction_is_saved_for_review(
        self, webhook_client, configured_secret, db
    ):
        payload = valid_payload(
            sender_number="09999999999",
            amount="999.00",
            transaction_id="TX-UNMATCHED",
        )
        resp = webhook_client.post(
            WEBHOOK_URL,
            data=payload,
            format="json",
            HTTP_X_VODAFONE_SIGNATURE=sign(payload),
        )
        assert resp.status_code == 200
        assert resp.data["status"] == "unmatched"

    def test_duplicate_transaction_is_ignored(
        self, webhook_client, configured_secret, db, basic_plan
    ):
        from payments.models import PaymentTransaction
        from payments.services.payment_service import PaymentService

        # First, create a transaction directly
        PaymentTransaction.objects.create(
            id="TX-DUP",
            amount=200,
            sender_number="01012345678",
            raw_sms="...",
            order=None,
        )

        # Now send the same transaction_id via webhook
        payload = valid_payload(transaction_id="TX-DUP")
        resp = webhook_client.post(
            WEBHOOK_URL,
            data=payload,
            format="json",
            HTTP_X_VODAFONE_SIGNATURE=sign(payload),
        )
        assert resp.status_code == 200
        assert resp.data["status"] == "ignored"