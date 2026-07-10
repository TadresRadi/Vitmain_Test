import hmac
import logging

from django.conf import settings
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..services.payment_matching_service import PaymentMatchingService


logger = logging.getLogger(__name__)


class VodafoneCashWebhookView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        configured_token = settings.VODAFONE_WEBHOOK_SECRET_TOKEN
        authorization = request.headers.get("Authorization", "")

        expected = f"Bearer {configured_token}"

        if not configured_token or not hmac.compare_digest(
            authorization,
            expected,
        ):
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

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