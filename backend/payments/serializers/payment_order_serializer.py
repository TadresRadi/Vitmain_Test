from decimal import Decimal

from rest_framework import serializers

from ..models.payment_order import PaymentOrder


class PaymentOrderSerializer(serializers.ModelSerializer):
    remaining_amount = serializers.SerializerMethodField()
    payment_completed = serializers.SerializerMethodField()

    class Meta:
        model = PaymentOrder
        fields = [
            "id",
            "user",
            "plan",
            "expected_amount",
            "expected_sender_number",
            "received_amount",
            "extra_amount",
            "remaining_amount",
            "payment_completed",
            "status",
            "reference_code",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_remaining_amount(self, obj):
        # Coerce to Decimal — freshly-created orders may have float defaults
        # (0.0) instead of Decimal('0.00') until they're re-fetched from the DB.
        expected = Decimal(str(obj.expected_amount))
        received = Decimal(str(obj.received_amount))
        remaining = expected - received
        return max(remaining, Decimal("0.00"))

    def get_payment_completed(self, obj):
        return obj.status == PaymentOrder.Status.COMPLETED