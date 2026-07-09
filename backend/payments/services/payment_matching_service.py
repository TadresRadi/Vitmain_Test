from django.db import transaction
from ..models.payment_order import PaymentOrder
from ..models.payment_transaction import PaymentTransaction
from .payment_service import PaymentService
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class PaymentMatchingService:
    
    @staticmethod
    def process_incoming_transaction(sender_number, amount, transaction_id, raw_sms, reference_code=None):
        # Enforce Idempotency / Prevent Duplicate SMS Processing
        existing_tx = PaymentTransaction.objects.filter(id=transaction_id).first()
        if existing_tx:
            return {
                'status': 'ignored',
                'message': 'Duplicate transaction. Already processed.',
                'linked_order_id': str(existing_tx.order.id) if existing_tx.order else None
            }

        numeric_amount = Decimal(str(amount))
        matched_order = None
        match_reason = ""

        # Priority 1: Match by reference_code
        if reference_code:
            matched_order = PaymentOrder.objects.select_for_update().filter(
                reference_code=reference_code,
                status__in=[PaymentOrder.Status.PENDING, PaymentOrder.Status.PARTIAL]
            ).first()
            if matched_order:
                match_reason = "Priority 1: Reference Code Match"

        # Priority 2: Match by sender_number + exact amount
        if not matched_order:
            matched_order = PaymentOrder.objects.select_for_update().filter(
                expected_sender_number=sender_number,
                expected_amount=numeric_amount,
                status__in=[PaymentOrder.Status.PENDING, PaymentOrder.Status.PARTIAL]
            ).first()
            if matched_order:
                match_reason = "Priority 2: Expected Sender Number + Exact Amount Match"

        # Priority 2 Fallback: Match by sender_number to any active order (handling different amounts)
        if not matched_order:
            matched_order = PaymentOrder.objects.select_for_update().filter(
                expected_sender_number=sender_number,
                status__in=[PaymentOrder.Status.PENDING, PaymentOrder.Status.PARTIAL]
            ).first()
            if matched_order:
                match_reason = "Priority 2 Fallback: Sender Number Match"

        # Save Transaction Record
        if matched_order:

            with transaction.atomic():

        # Save transaction record
                PaymentTransaction.objects.create(
                    id=transaction_id,
                    order=matched_order,
                    amount=numeric_amount,
                    sender_number=sender_number,
                    raw_sms=raw_sms
                )

        # Add new payment amount
        matched_order.received_amount += numeric_amount


        # Payment completed
        if matched_order.received_amount >= matched_order.expected_amount:

            # Calculate extra money
            matched_order.extra_amount = (
                matched_order.received_amount -
                matched_order.expected_amount
            )

            matched_order.status = PaymentOrder.Status.COMPLETED

            PaymentService.activate_subscription(matched_order)


        # Partial payment
        else:

            matched_order.status = PaymentOrder.Status.PARTIAL


        matched_order.save()
        return {
                'status': 'matched',
                'match_reason': match_reason,
                'order_status': matched_order.status,
                'received_amount': float(matched_order.received_amount),
                'expected_amount': float(matched_order.expected_amount),
                'order_id': str(matched_order.id)   # <-- ADDED
            }
