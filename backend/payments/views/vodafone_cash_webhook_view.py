# backend/payments/views/vodafone_cash_webhook_view.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import transaction
from django.conf import settings
from ..services.payment_matching_service import PaymentMatchingService
import logging

logger = logging.getLogger(__name__)


class VodafoneCashWebhookView(APIView):
    """
    Webhook endpoint for receiving Vodafone Cash SMS payment notifications
    from Android app (e.g., via ngrok).

    Expects Authorization: Bearer {VODAFONE_WEBHOOK_SECRET_TOKEN}
    """
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        logger.info("=== VODAFONE WEBHOOK RECEIVED ===")

        # Authentication via Bearer token
        auth_header = request.headers.get('Authorization', '')
        webhook_token = getattr(settings, 'VODAFONE_WEBHOOK_SECRET_TOKEN', None)

        if not webhook_token:
            logger.error("VODAFONE_WEBHOOK_SECRET_TOKEN not configured in backend settings")
            return Response(
                {'error': 'Server configuration error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        expected_auth = f"Bearer {webhook_token}"
        if auth_header != expected_auth:
            logger.warning(f"Unauthorized webhook attempt. Got: {auth_header[:20]}...")
            return Response(
                {'error': 'Unauthorized'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Validate required fields
        required_fields = ['sender_number', 'amount', 'transaction_id', 'raw_sms']
        missing = [f for f in required_fields if f not in request.data]

        if missing:
            logger.error(f"Webhook missing fields: {missing}")
            return Response(
                {'error': f'Missing required fields: {missing}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            sender_number = request.data.get('sender_number')
            amount = request.data.get('amount')
            transaction_id = request.data.get('transaction_id')
            raw_sms = request.data.get('raw_sms')
            reference_code = request.data.get('reference_code')

            logger.info(f"Processing: TxID={transaction_id}, Amount={amount} EGP, From={sender_number}")

            # Process transaction atomically
            with transaction.atomic():
                result = PaymentMatchingService.process_incoming_transaction(
                    sender_number=sender_number,
                    amount=amount,
                    transaction_id=transaction_id,
                    raw_sms=raw_sms,
                    reference_code=reference_code
                )

            # If we matched an order, attach a frontend next_url so callers can open it
            order_id = None
            if isinstance(result, dict):
                order_id = result.get('order_id') or result.get('linked_order_id')

            frontend_base = getattr(settings, 'FRONTEND_BASE_URL', '').rstrip('/')
            if not frontend_base:
                frontend_base = f"{request.scheme}://{request.get_host()}"

            if order_id:
                # Adjust path to match your frontend routing if needed
                result['next_url'] = f"{frontend_base}/orders/{order_id}/next"

            logger.info(f"Webhook result: {result}")
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Failed to process webhook', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )