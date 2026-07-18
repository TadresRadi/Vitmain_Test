"""
Admin endpoints for reviewing ambiguous payment transactions.
"""
import logging
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from users.permissions import IsSuperAdmin
from payments.models import PaymentTransaction, PaymentOrder
from payments.services.payment_service import PaymentService

logger = logging.getLogger(__name__)


class AdminPaymentReviewListView(APIView):
    """
    List payment transactions that need manual review.

    GET /api/payments/admin/review/
    Returns transactions where needs_review=True and review_status='pending'.
    """
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        transactions = PaymentTransaction.objects.filter(
            needs_review=True,
            review_status=PaymentTransaction.ReviewStatus.PENDING,
        ).order_by('-created_at')

        data = []
        for tx in transactions:
            data.append({
                'id': tx.id,
                'amount': str(tx.amount),
                'sender_number': tx.sender_number,
                'raw_sms': tx.raw_sms,
                'order_id': str(tx.order_id) if tx.order_id else None,
                'reference_code': tx.order.reference_code if tx.order else None,
                'expected_amount': str(tx.order.expected_amount) if tx.order else None,
                'expected_sender_number': tx.order.expected_sender_number if tx.order else None,
                'created_at': tx.created_at.isoformat(),
            })

        return Response({'transactions': data, 'count': len(data)})


class AdminPaymentReviewActionView(APIView):
    """
    Approve or reject a payment transaction under review.

    POST /api/payments/admin/review/<transaction_id>/
    {
        "action": "approve" | "reject",
        "notes": "optional reason"
    }
    """
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

    def post(self, request, transaction_id):
        action = request.data.get('action')
        notes = request.data.get('notes', '')

        if action not in ('approve', 'reject'):
            return Response(
                {'error': 'action must be "approve" or "reject"'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            tx = PaymentTransaction.objects.get(id=transaction_id)
        except PaymentTransaction.DoesNotExist:
            return Response(
                {'error': 'Transaction not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not tx.needs_review:
            return Response(
                {'error': 'This transaction does not need review'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if tx.review_status != PaymentTransaction.ReviewStatus.PENDING:
            return Response(
                {'error': f'Transaction already {tx.review_status}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tx.review_status = (
            PaymentTransaction.ReviewStatus.APPROVED
            if action == 'approve'
            else PaymentTransaction.ReviewStatus.REJECTED
        )
        tx.review_notes = notes
        tx.reviewed_by = request.user
        tx.reviewed_at = timezone.now()
        tx.save(update_fields=[
            'review_status', 'review_notes', 'reviewed_by', 'reviewed_at',
        ])

        if action == 'approve' and tx.order:
            # Now complete the order
            tx.order.received_amount += tx.amount
            if tx.order.received_amount >= tx.order.expected_amount:
                tx.order.extra_amount = tx.order.received_amount - tx.order.expected_amount
                tx.order.status = PaymentOrder.Status.COMPLETED
                PaymentService.activate_subscription(tx.order)
            else:
                tx.order.status = PaymentOrder.Status.PARTIAL
            tx.order.save(update_fields=[
                'received_amount', 'extra_amount', 'status', 'updated_at',
            ])

        logger.info(
            "Payment transaction %s %s by admin %s",
            transaction_id, action, request.user.email,
        )

        return Response({
            'message': f'Transaction {action}d successfully',
            'transaction_id': tx.id,
            'review_status': tx.review_status,
        })