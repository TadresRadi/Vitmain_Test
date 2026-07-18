import hashlib
import hmac
import logging

from django.conf import settings
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..services.payment_matching_service import PaymentMatchingService


logger = logging.getLogger(__name__)


class VodafoneCashWebhookView(APIView):
    """
    Vodafone Cash webhook receiver.

    Authenticates the request by computing HMAC-SHA256 over the raw
    request body using the shared secret (VODAFONE_WEBHOOK_SECRET_TOKEN)
    and comparing it to the signature in the X-Vodafone-Signature header.

    Expected headers:
        X-Vodafone-Signature: <hex HMAC-SHA256 of raw body>
        Content-Type: application/json

    Expected body:
        {
            "sender_number": "01012345678",
            "amount": "200.00",
            "transaction_id": "TX123456",
            "raw_sms": "...",
            "reference_code": "VITMAIN-ABC123"  # optional
        }
    """

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        configured_secret = settings.VODAFONE_WEBHOOK_SECRET_TOKEN
        signature_header = request.headers.get("X-Vodafone-Signature", "")

        if not configured_secret:
            logger.error("VODAFONE_WEBHOOK_SECRET_TOKEN not configured")
            return Response(
                {"error": "Webhook secret not configured"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Read the raw body — DRF's request.data has already parsed it,
        # but we need the raw bytes for signature verification.
        raw_body = request.body
        if not raw_body:
            return Response(
                {"error": "Empty request body"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Compute expected HMAC-SHA256 over the raw body
        expected_signature = hmac.new(
            key=configured_secret.encode("utf-8"),
            msg=raw_body,
            digestmod=hashlib.sha256,
        ).hexdigest()

        # Constant-time comparison to prevent timing attacks
        if not signature_header or not hmac.compare_digest(
            signature_header,
            expected_signature,
        ):
            logger.warning(
                "Vodafone webhook signature mismatch (got %s, expected %s)",
                signature_header[:8] + "..." if signature_header else "(empty)",
                expected_signature[:8] + "...",
            )
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Signature is valid — now validate the payload
        required_fields = [
            "sender_number",
            "amount",
            "transaction_id",
            "raw_sms",
        ]
        missing_fields = [
            field
            for field in required_fields
            if request.data.get(field) in (None, "")
        ]

        if missing_fields:
            return Response(
                {
                    "error": "Missing required fields.",
                    "fields": missing_fields,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = PaymentMatchingService.process_incoming_transaction(
                sender_number=request.data["sender_number"],
                amount=request.data["amount"],
                transaction_id=request.data["transaction_id"],
                raw_sms=request.data["raw_sms"],
                reference_code=request.data.get("reference_code"),
            )
        except ValueError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            logger.exception("Vodafone payment webhook processing failed")
            return Response(
                {"error": "Failed to process webhook."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(result, status=status.HTTP_200_OK)