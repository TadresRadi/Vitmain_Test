import secrets
import re

from django.db import DatabaseError, IntegrityError, transaction
import logging

logger = logging.getLogger(__name__)
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from decimal import Decimal
from subscriptions.models import Plan

from ..models.payment_order import PaymentOrder
from ..serializers.payment_order_serializer import PaymentOrderSerializer


class CreatePaymentOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        sender_number = request.data.get("expected_sender_number")
        plan_slug = request.data.get("plan")

        if not sender_number:
            return Response(
                {"error": "expected_sender_number is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not plan_slug:
            return Response(
                {"error": "plan is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        clean_number = re.sub(r"\s+", "", str(sender_number))

        if not re.fullmatch(r"(010|011|012|015)\d{8}", clean_number):
            return Response(
                {"error": "Invalid Egyptian mobile number."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            plan = Plan.objects.get(slug=plan_slug)
        except Plan.DoesNotExist:
            return Response(
                {"error": "Plan not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        existing_order = (
            PaymentOrder.objects
            .filter(
                user=request.user,
                plan=plan.slug,
                status__in=[
                    PaymentOrder.Status.PENDING,
                    PaymentOrder.Status.PARTIAL,
                ],
            )
            .order_by("-created_at")
            .first()
        )

        if existing_order:
            # Update the expected sender if the user corrects their number.
            if existing_order.expected_sender_number != clean_number:
                existing_order.expected_sender_number = clean_number
                existing_order.save(
                    update_fields=[
                        "expected_sender_number",
                        "updated_at",
                    ]
                )

            return Response(
                self._response_data(existing_order),
                status=status.HTTP_200_OK,
            )

        try:
            with transaction.atomic():
                payment_order = PaymentOrder.objects.create(
                    user=request.user,
                    plan=plan.slug,
                    expected_amount=plan.price,
                    expected_sender_number=clean_number,
                    reference_code=self._create_reference_code(),
                )
        except IntegrityError:
            return Response(
                {"error": "Could not create a payment order. Please retry."},
                status=status.HTTP_409_CONFLICT,
            )
        except DatabaseError as exc:
            # Catches OperationalError (missing column/table), ProgrammingError, etc.
            # These are not the user's fault — they indicate a migration or schema issue.
            logger.exception(
                "Database error creating payment order for user %s",
                request.user.id,
            )
            from django.conf import settings
            return Response(
                {
                    "error": "Payment service is temporarily unavailable.",
                    "detail": str(exc) if settings.DEBUG else None,
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            return Response(
                self._response_data(payment_order),
                status=status.HTTP_201_CREATED,
            )
        except Exception:
            # If the serializer fails for any reason, log it and return 503
            # instead of a bare 500 with no diagnostic info.
            logger.exception(
                "Failed to serialize payment order %s",
                payment_order.id,
            )
            return Response(
                {"error": "Payment order created but response could not be generated."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

    @staticmethod
    def _create_reference_code():
        for _ in range(20):
            reference_code = f"VFC{secrets.randbelow(900000) + 100000}"

            if not PaymentOrder.objects.filter(
                reference_code=reference_code
            ).exists():
                return reference_code

        raise IntegrityError("Could not generate a unique reference code")

    @staticmethod
    def _response_data(order):
        from django.conf import settings

        receiver_number = settings.VODAFONE_RECEIVER_NUMBER
        remaining = max(
            order.expected_amount - order.received_amount,
            Decimal("0.00"),
        )
        print(type(order.expected_amount), order.expected_amount)
        print(type(order.received_amount), order.received_amount)

        data = PaymentOrderSerializer(order).data
        data.update(
            {
                "receiver_number": receiver_number,
                "amount": remaining,
                "remaining_amount": remaining,
                "payment_instructions": (
                    f"Send exactly {remaining} EGP "
                    f"to {receiver_number}."
                ),
            }
        )
        return data