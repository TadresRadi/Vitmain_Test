"""
Tests for PaymentMatchingService.process_incoming_transaction().

This is the most critical test file in the project — it verifies that
money is matched to the correct order, duplicates are ignored, partial
payments accumulate correctly, and validation rejects bad input.

Run: pytest payments/tests/test_payment_matching_service.py -v
"""
import pytest
from decimal import Decimal

from payments.models import PaymentOrder, PaymentTransaction
from payments.services.payment_matching_service import PaymentMatchingService
from subscriptions.models import Subscription
from tests.factories import (
    UserFactory,
)


# ============================================================================
# Helpers
# ============================================================================

def _create_order(user, expected_amount=Decimal("200.00"),
                  sender="01012345678", reference_code="VFC100001",
                  status=PaymentOrder.Status.PENDING):
    """Create a PaymentOrder with sensible defaults."""
    return PaymentOrder.objects.create(
        user=user,
        plan="basic",
        expected_amount=expected_amount,
        expected_sender_number=sender,
        reference_code=reference_code,
        status=status,
    )


def _process(sender_number="01012345678", amount="200",
             transaction_id="TX001", raw_sms="sms body",
             reference_code=None):
    """Call the service with the given parameters."""
    return PaymentMatchingService.process_incoming_transaction(
        sender_number=sender_number,
        amount=amount,
        transaction_id=transaction_id,
        raw_sms=raw_sms,
        reference_code=reference_code,
    )


# ============================================================================
# Priority 1: Reference code matching
# ============================================================================

@pytest.mark.django_db
@pytest.mark.money
def test_priority1_reference_code_match_completes_order(basic_plan):
    """A transaction with a matching reference code should complete the order."""
    user = UserFactory()
    order = _create_order(user, reference_code="VFC100001")

    result = _process(
        sender_number="01012345678",
        amount="200",
        transaction_id="TX001",
        reference_code="VFC100001",
    )

    assert result["status"] == "matched"
    assert "Reference Code" in result["match_reason"]
    assert result["order_status"] == "completed"
    assert result["received_amount"] == 200.0
    assert result["extra_amount"] == 0.0

    order.refresh_from_db()
    assert order.status == "completed"
    assert order.received_amount == Decimal("200.00")

    # Subscription should be activated
    sub = Subscription.objects.get(user=user)
    assert sub.active is True
    assert sub.plan.slug == "basic"


# ============================================================================
# Partial payments
# ============================================================================

@pytest.mark.django_db
@pytest.mark.money
def test_partial_payment_sets_partial_status(basic_plan):
    """A payment less than expected_amount should set status to PARTIAL."""
    user = UserFactory()
    order = _create_order(user, expected_amount=Decimal("200.00"))

    result = _process(amount="100", transaction_id="TX001")

    assert result["status"] == "matched"
    assert result["order_status"] == "partial"

    order.refresh_from_db()
    assert order.status == "partial"
    assert order.received_amount == Decimal("100.00")

    # No subscription should be created for partial payments
    assert not Subscription.objects.filter(user=user).exists()


@pytest.mark.django_db
@pytest.mark.money
def test_two_partial_payments_complete_order(basic_plan):
    """Two partial payments that sum to expected_amount should complete the order."""
    user = UserFactory()
    order = _create_order(user, expected_amount=Decimal("200.00"))

    # First payment — partial
    _process(amount="120", transaction_id="TX001")
    order.refresh_from_db()
    assert order.status == "partial"

    # Second payment — completes the order
    result = _process(amount="80", transaction_id="TX002")
    assert result["status"] == "matched"
    assert result["order_status"] == "completed"

    order.refresh_from_db()
    assert order.status == "completed"
    assert order.received_amount == Decimal("200.00")

    # Subscription should now exist
    assert Subscription.objects.filter(user=user).exists()


# ============================================================================
# Overpayment
# ============================================================================

@pytest.mark.django_db
@pytest.mark.money
def test_overpayment_records_extra_amount(basic_plan):
    """An overpayment should complete the order and record the extra amount."""
    user = UserFactory()
    order = _create_order(user, expected_amount=Decimal("200.00"))

    result = _process(amount="250", transaction_id="TX001")

    assert result["status"] == "matched"
    assert result["order_status"] == "completed"
    assert result["received_amount"] == 250.0
    assert result["extra_amount"] == 50.0

    order.refresh_from_db()
    assert order.received_amount == Decimal("250.00")
    assert order.extra_amount == Decimal("50.00")


# ============================================================================
# Priority 2: Sender + amount matching
# ============================================================================

@pytest.mark.django_db
@pytest.mark.money
def test_priority2_sender_plus_amount_match(basic_plan):
    """Without a reference code, match by sender_number + exact amount."""
    user = UserFactory()
    order = _create_order(user, sender="01011111111",
                          expected_amount=Decimal("200.00"))

    result = _process(
        sender_number="01011111111",
        amount="200",
        transaction_id="TX001",
    )

    assert result["status"] == "matched"
    assert "Priority 2" in result["match_reason"]
    assert "Fallback" not in result["match_reason"]
    assert result["order_status"] == "completed"


# ============================================================================
# Priority 2 Fallback: Sender-only matching
# ============================================================================

@pytest.mark.django_db
@pytest.mark.money
def test_priority2_fallback_sender_only_match(basic_plan):
    """If sender+amount don't match, fall back to sender-only (any amount)."""
    user = UserFactory()
    # Order expects 200, but we send 150 — won't match on amount
    order = _create_order(user, sender="01022222222",
                          expected_amount=Decimal("200.00"))

    result = _process(
        sender_number="01022222222",
        amount="150",
        transaction_id="TX001",
    )

    assert result["status"] == "matched"
    assert "Fallback" in result["match_reason"]
    assert result["order_status"] == "partial"  # 150 < 200


# ============================================================================
# FIFO ordering
# ============================================================================

@pytest.mark.django_db
@pytest.mark.money
def test_fifo_oldest_order_matched_first(basic_plan):
    """When multiple orders match, the oldest one should be matched first."""
    user = UserFactory()
    # Create two orders with the same sender and expected amount
    order1 = _create_order(user, sender="01033333333",
                          expected_amount=Decimal("200.00"),
                          reference_code="VFC100001")
    order2 = _create_order(user, sender="01033333333",
                          expected_amount=Decimal("200.00"),
                          reference_code="VFC100002")

    # order1 was created first (auto_now_add), so it should be matched
    result = _process(
        sender_number="01033333333",
        amount="200",
        transaction_id="TX001",
    )

    assert result["order_id"] == str(order1.id)


# ============================================================================
# Unmatched transactions
# ============================================================================

@pytest.mark.django_db
@pytest.mark.money
def test_unmatched_transaction_saved_for_review(basic_plan):
    """A transaction with no matching order should be saved for manual review."""
    result = _process(
        sender_number="01099999999",
        amount="200",
        transaction_id="TX001",
    )

    assert result["status"] == "unmatched"
    assert "manual review" in result["message"]

    tx = PaymentTransaction.objects.get(id="TX001")
    assert tx.order is None
    assert tx.amount == Decimal("200.00")


# ============================================================================
# Duplicate handling
# ============================================================================

@pytest.mark.django_db
@pytest.mark.money
def test_duplicate_transaction_id_returns_ignored(basic_plan):
    """A transaction with an already-used ID should be ignored."""
    user = UserFactory()
    order = _create_order(user)

    # First call — processes normally
    _process(transaction_id="DUP1", amount="200")

    # Second call with same transaction_id — should be ignored
    result = _process(transaction_id="DUP1", amount="200")

    assert result["status"] == "ignored"
    assert "Duplicate" in result["message"]
    assert result["linked_order_id"] == str(order.id)

    # Only one transaction should exist
    assert PaymentTransaction.objects.count() == 1


# ============================================================================
# Completed/Failed orders not re-matched
# ============================================================================

@pytest.mark.django_db
@pytest.mark.money
def test_completed_order_not_rematched(basic_plan):
    """A COMPLETED order should not be matched again."""
    user = UserFactory()
    order = _create_order(user, status=PaymentOrder.Status.COMPLETED,
                          reference_code="VFC100001")
    order.received_amount = Decimal("200.00")
    order.save()

    result = _process(
        amount="200",
        transaction_id="TX001",
        reference_code="VFC100001",
    )

    assert result["status"] == "unmatched"


@pytest.mark.django_db
@pytest.mark.money
def test_failed_order_not_rematched(basic_plan):
    """A FAILED order should not be matched."""
    user = UserFactory()
    order = _create_order(user, status=PaymentOrder.Status.FAILED,
                          reference_code="VFC100001")

    result = _process(
        amount="200",
        transaction_id="TX001",
        reference_code="VFC100001",
    )

    assert result["status"] == "unmatched"


# ============================================================================
# Input validation
# ============================================================================

@pytest.mark.django_db
@pytest.mark.money
def test_empty_transaction_id_raises_value_error():
    with pytest.raises(ValueError, match="transaction_id"):
        _process(transaction_id="", amount="200")


@pytest.mark.django_db
@pytest.mark.money
def test_empty_sender_number_raises_value_error():
    with pytest.raises(ValueError, match="sender_number"):
        _process(transaction_id="TX001", sender_number="", amount="200")


@pytest.mark.django_db
@pytest.mark.money
def test_zero_amount_raises_value_error():
    with pytest.raises(ValueError, match="greater than zero"):
        _process(transaction_id="TX001", amount="0")


@pytest.mark.django_db
@pytest.mark.money
def test_negative_amount_raises_value_error():
    with pytest.raises(ValueError, match="greater than zero"):
        _process(transaction_id="TX001", amount="-5")


@pytest.mark.django_db
@pytest.mark.money
def test_non_numeric_amount_raises_value_error():
    with pytest.raises(ValueError, match="valid number"):
        _process(transaction_id="TX001", amount="abc")


# ============================================================================
# Amount type flexibility
# ============================================================================

@pytest.mark.django_db
@pytest.mark.money
def test_amount_accepts_integer(basic_plan):
    """The service should accept int amounts."""
    user = UserFactory()
    _create_order(user, expected_amount=Decimal("200.00"))

    result = _process(amount=200, transaction_id="TX001")
    assert result["status"] == "matched"


@pytest.mark.django_db
@pytest.mark.money
def test_amount_accepts_float(basic_plan):
    """The service should accept float amounts."""
    user = UserFactory()
    _create_order(user, expected_amount=Decimal("200.00"))

    result = _process(amount=200.0, transaction_id="TX001")
    assert result["status"] == "matched"


@pytest.mark.django_db
@pytest.mark.money
def test_amount_accepts_decimal_string(basic_plan):
    """The service should accept decimal string amounts."""
    user = UserFactory()
    _create_order(user, expected_amount=Decimal("200.00"))

    result = _process(amount="200.00", transaction_id="TX001")
    assert result["status"] == "matched"


# ============================================================================
# Whitespace handling
# ============================================================================

@pytest.mark.django_db
@pytest.mark.money
def test_whitespace_in_inputs_is_stripped(basic_plan):
    """Leading/trailing whitespace in inputs should be stripped."""
    user = UserFactory()
    order = _create_order(user, reference_code="VFC100001")

    result = _process(
        transaction_id="  TX001  ",
        sender_number="  01012345678  ",
        amount="200",
        reference_code="  VFC100001  ",
    )

    assert result["status"] == "matched"

    # Verify the stored transaction has stripped values
    tx = PaymentTransaction.objects.get(id="TX001")
    assert tx.sender_number == "01012345678"


# ============================================================================
# Subscription activation
# ============================================================================

@pytest.mark.django_db
@pytest.mark.money
def test_subscription_activated_on_completed_payment(basic_plan):
    """When a payment completes, the user's subscription should be activated."""
    user = UserFactory()
    _create_order(user, reference_code="VFC100001")

    _process(
        amount="200",
        transaction_id="TX001",
        reference_code="VFC100001",
    )

    sub = Subscription.objects.get(user=user)
    assert sub.active is True
    assert sub.plan.slug == "basic"


@pytest.mark.django_db
@pytest.mark.money
def test_subscription_not_activated_on_partial_payment(basic_plan):
    """Partial payments should NOT activate a subscription."""
    user = UserFactory()
    _create_order(user, expected_amount=Decimal("200.00"))

    _process(amount="100", transaction_id="TX001")

    assert not Subscription.objects.filter(user=user).exists()