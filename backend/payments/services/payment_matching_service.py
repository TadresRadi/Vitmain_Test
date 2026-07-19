import logging
from decimal import Decimal, InvalidOperation

from django.db import IntegrityError, transaction

from ..models.payment_order import PaymentOrder
from ..models.payment_transaction import PaymentTransaction
from .payment_service import PaymentService


logger = logging.getLogger(__name__)


class PaymentMatchingService:

    @staticmethod
    @transaction.atomic
    def process_incoming_transaction(
        sender_number,
        amount,
        transaction_id,
        raw_sms,
        reference_code=None,
    ):
        transaction_id = str(transaction_id).strip()
        sender_number = str(sender_number).strip()
        reference_code = (
            str(reference_code).strip() if reference_code else None
        )

        if not transaction_id:
            raise ValueError("transaction_id is required")

        if not sender_number:
            raise ValueError("sender_number is required")

        try:
            numeric_amount = Decimal(str(amount))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValueError("amount must be a valid number") from exc

        if numeric_amount <= 0:
            raise ValueError("amount must be greater than zero")

        existing_transaction = (
            PaymentTransaction.objects
            .select_related("order")
            .filter(pk=transaction_id)
            .first()
        )

        if existing_transaction:
            return {
                "status": "ignored",
                "message": "Duplicate transaction. Already processed.",
                "linked_order_id": (
                    str(existing_transaction.order_id)
                    if existing_transaction.order_id
                    else None
                ),
            }

        matched_order = None
        match_reason = None
        active_statuses = [
            PaymentOrder.Status.PENDING,
            PaymentOrder.Status.PARTIAL,
        ]

        if reference_code:
            matched_order = (
                PaymentOrder.objects
                .select_for_update()
                .filter(
                    reference_code=reference_code,
                    status__in=active_statuses,
                )
                .first()
            )

            if matched_order:
                match_reason = "Priority 1: Reference Code Match"

        if matched_order is None:
            matched_order = (
                PaymentOrder.objects
                .select_for_update()
                .filter(
                    expected_sender_number=sender_number,
                    expected_amount=numeric_amount,
                    status__in=active_statuses,
                )
                .order_by("created_at")
                .first()
            )

            if matched_order:
                match_reason = (
                    "Priority 2: Expected Sender Number "
                    "+ Exact Amount Match"
                )

        needs_review = False
        if matched_order is None:
            matched_order = (
                PaymentOrder.objects
                .select_for_update()
                .filter(
                    expected_sender_number=sender_number,
                    status__in=active_statuses,
                )
                .order_by("created_at")
                .first()
            )

            if matched_order:
                match_reason = "Priority 2 Fallback: Sender Number Match (needs review)"
                needs_review = True

        try:
            with transaction.atomic():
                payment_transaction = PaymentTransaction.objects.create(
                    id=transaction_id,
                    order=matched_order,
                    amount=numeric_amount,
                    sender_number=sender_number,
                    raw_sms=raw_sms,
                    needs_review=needs_review,
                )
        except IntegrityError:
            existing_transaction = (
                PaymentTransaction.objects
                .select_related("order")
                .get(pk=transaction_id)
            )

            return {
                "status": "ignored",
                "message": "Duplicate transaction. Already processed.",
                "linked_order_id": (
                    str(existing_transaction.order_id)
                    if existing_transaction.order_id
                    else None
                ),
            }

        if matched_order is None:
            logger.warning(
                "Payment transaction %s could not be matched to an order",
                payment_transaction.pk,
            )

            return {
                "status": "unmatched",
                "message": "Transaction saved for manual review.",
                "transaction_id": payment_transaction.pk,
            }

        if needs_review:
    # لا تضيف المبلغ أثناء انتظار المراجعة
            matched_order.extra_amount = Decimal("0.00")
            matched_order.status = PaymentOrder.Status.PARTIAL

            logger.warning(
                "Payment transaction %s matched to order %s via fallback "
                "(sender-only) — flagged for manual review",
                payment_transaction.pk,
                matched_order.id,)
        else:
            matched_order.received_amount += numeric_amount

            if matched_order.received_amount >= matched_order.expected_amount:
                matched_order.extra_amount = (
                matched_order.received_amount
                - matched_order.expected_amount)
                matched_order.status = PaymentOrder.Status.COMPLETED
                PaymentService.activate_subscription(matched_order)
            else:
                matched_order.extra_amount = Decimal("0.00")
                matched_order.status = PaymentOrder.Status.PARTIAL


        matched_order.save(
            update_fields=[
                "received_amount",
                "extra_amount",
                "status",
                "updated_at",
            ]
        )

        return {
            "status": "matched",
            "match_reason": match_reason,
            "order_status": matched_order.status,
            "received_amount": float(matched_order.received_amount),
            "expected_amount": float(matched_order.expected_amount),
            "extra_amount": float(matched_order.extra_amount),
            "order_id": str(matched_order.id),
            "needs_review": needs_review,
        }
