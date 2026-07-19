"""
Tests for the manual payment review queue.
"""
import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from payments.models import PaymentOrder, PaymentTransaction
from payments.services.payment_matching_service import PaymentMatchingService

User = get_user_model()

# Shared dummy passwords for payment-review tests. Not real credentials.
ADMIN_PASSWORD = "adminpass123"  # nosec B105 - test fixture
TEST_PASSWORD = "pass123"  # nosec B105 - test fixture


@pytest.fixture
def super_admin(db):
    return User.objects.create_user(
        email="admin@example.com",
        password=ADMIN_PASSWORD,
        role="super_admin",
        is_staff=True,
        is_superuser=True,
        is_email_verified=True,
    )


@pytest.fixture
def admin_client(super_admin):
    client = APIClient()
    client.force_authenticate(user=super_admin)
    return client


@pytest.fixture
def pending_order(basic_plan, db):
    from payments.services.payment_service import PaymentService
    user = User.objects.create_user(
        email="buyer@example.com",
        password=TEST_PASSWORD,
        is_email_verified=True,
    )
    return PaymentOrder.objects.create(
        user=user,
        plan="basic",
        expected_amount=Decimal("200.00"),
        expected_sender_number="01012345678",
        reference_code="VIT-TEST-001",
        status=PaymentOrder.Status.PENDING,
    )

def make_order(amount, sender, ref_code):
    user = User.objects.create_user(
        email=f"buyer-{ref_code}@example.com",
        password=TEST_PASSWORD,
        is_email_verified=True,
    )

    return PaymentOrder.objects.create(
        user=user,
        plan="basic",
        expected_amount=Decimal(amount),
        expected_sender_number=sender,
        reference_code=ref_code,
        status=PaymentOrder.Status.PENDING,
    )

@pytest.mark.django_db
class TestPaymentReviewFlagging:
    def test_reference_code_match_does_not_flag_for_review(self, pending_order):
        """Priority 1 match (reference code) should NOT need review."""
        result = PaymentMatchingService.process_incoming_transaction(
            sender_number="01012345678",
            amount="200.00",
            transaction_id="TX-REF-001",
            raw_sms="...",
            reference_code="VIT-TEST-001",
        )
        assert result["status"] == "matched"
        assert result.get("needs_review") is False

        tx = PaymentTransaction.objects.get(id="TX-REF-001")
        assert tx.needs_review is False

    def test_sender_only_match_flags_for_review(self, pending_order):
        """Priority 2 fallback (sender only, no reference code) should flag for review."""
        result = PaymentMatchingService.process_incoming_transaction(
            sender_number="01012345678",
            amount="150.00",
            transaction_id="TX-SENDER-001",
            raw_sms="...",
            reference_code=None,
        )
        assert result["status"] == "matched"
        assert result.get("needs_review") is True

        tx = PaymentTransaction.objects.get(id="TX-SENDER-001")
        assert tx.needs_review is True
        assert tx.review_status == PaymentTransaction.ReviewStatus.PENDING

        # Order should NOT be completed automatically
        pending_order.refresh_from_db()
        assert pending_order.status == PaymentOrder.Status.PARTIAL

    def test_sender_plus_amount_match_does_not_flag(self, pending_order):
        """Priority 2 (sender + exact amount) should NOT need review."""
        result = PaymentMatchingService.process_incoming_transaction(
            sender_number="01012345678",
            amount="200.00",
            transaction_id="TX-EXACT-001",
            raw_sms="...",
            reference_code=None,
        )
        assert result["status"] == "matched"
        assert result.get("needs_review") is False


@pytest.mark.django_db
class TestAdminReviewEndpoints:
    def test_list_review_queue(self, admin_client, pending_order):
        # Create a transaction that needs review
        PaymentMatchingService.process_incoming_transaction(
            sender_number="01012345678",
            amount="150.00",
            transaction_id="TX-REVIEW-001",
            raw_sms="...",
            reference_code=None,
        )

        resp = admin_client.get("/api/payments/admin/review/")
        assert resp.status_code == 200
        assert resp.data["count"] == 1
        assert resp.data["transactions"][0]["id"] == "TX-REVIEW-001"

    def test_review_queue_excludes_approved(self, admin_client, pending_order):
        PaymentMatchingService.process_incoming_transaction(
            sender_number="01012345678",
            amount="150.00",
            transaction_id="TX-REVIEW-002",
            raw_sms="...",
            reference_code=None,
        )

        # Approve it
        admin_client.post(
            "/api/payments/admin/review/TX-REVIEW-002/",
            {"action": "approve"},
            format="json",
        )

        # List should now be empty
        resp = admin_client.get("/api/payments/admin/review/")
        assert resp.data["count"] == 0

    def test_approve_applies_reviewed_payment(self, admin_client):
        order = make_order("200.00", "01012345678", "VIT-APPROVE-001")

        PaymentMatchingService.process_incoming_transaction(
            sender_number="01012345678",
            amount="150.00",      # Amount مختلف -> Sender Only Fallback
            transaction_id="TX-APPROVE-001",
            raw_sms="...",
            reference_code=None,
        )

        resp = admin_client.post(
            "/api/payments/admin/review/TX-APPROVE-001/",
            {"action": "approve", "notes": "Verified by phone"},
            format="json",
        )

        order.refresh_from_db()

        assert order.received_amount == Decimal("150.00")
        assert order.status == PaymentOrder.Status.PARTIAL

        assert resp.status_code == 200

        order.refresh_from_db()

        assert order.received_amount == Decimal("150.00")
        assert order.status == PaymentOrder.Status.PARTIAL

        tx = PaymentTransaction.objects.get(id="TX-APPROVE-001")
        assert tx.review_status == PaymentTransaction.ReviewStatus.APPROVED

        tx = PaymentTransaction.objects.get(id="TX-APPROVE-001")
        assert tx.review_status == PaymentTransaction.ReviewStatus.APPROVED

    def test_reject_does_not_complete_order(self, admin_client):
        order = make_order("200.00", "01012345678", "VIT-REJECT-001")

        PaymentMatchingService.process_incoming_transaction(
            sender_number="01012345678",
            amount="150.00",
            transaction_id="TX-REJECT-001",
            raw_sms="...",
            reference_code=None,
        )

        resp = admin_client.post(
            "/api/payments/admin/review/TX-REJECT-001/",
            {"action": "reject", "notes": "Wrong sender"},
            format="json",
        )

        assert resp.status_code == 200

        order.refresh_from_db()

        assert order.received_amount == Decimal("0.00")
        assert order.status == PaymentOrder.Status.PARTIAL

        tx = PaymentTransaction.objects.get(id="TX-REJECT-001")
        assert tx.review_status == PaymentTransaction.ReviewStatus.REJECTED

    def test_invalid_action_returns_400(self, admin_client, pending_order):
        PaymentMatchingService.process_incoming_transaction(
            sender_number="01012345678",
            amount="150.00",
            transaction_id="TX-INVALID-001",
            raw_sms="...",
            reference_code=None,
        )

        resp = admin_client.post(
            "/api/payments/admin/review/TX-INVALID-001/",
            {"action": "invalid"},
            format="json",
        )
        assert resp.status_code == 400

    def test_non_admin_cannot_access_review_queue(self, basic_plan, db):
        user = User.objects.create_user(
            email="regular@example.com",
            password=TEST_PASSWORD,
            role="user",
            is_email_verified=True,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        resp = client.get("/api/payments/admin/review/")
        assert resp.status_code == 403

    def test_nonexistent_transaction_returns_404(self, admin_client):
        resp = admin_client.post(
            "/api/payments/admin/review/NONEXISTENT/",
            {"action": "approve"},
            format="json",
        )
        assert resp.status_code == 404