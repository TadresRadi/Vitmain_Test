from rest_framework import serializers
from ..models.payment_order import PaymentOrder


class PaymentOrderSerializer(serializers.ModelSerializer):

    remaining_amount = serializers.SerializerMethodField()
    payment_completed = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()
    class Meta:
        model = PaymentOrder
        fields = [
            'id',
            'user',
            'plan',
            'expected_amount',
            'expected_sender_number',
            'received_amount',
            'remaining_amount',
            'payment_completed',
            'status',
            'reference_code',
            'created_at',
            'updated_at'
        ]

        read_only_fields = [
            'id',
            'user',
            'expected_amount',
            'received_amount',
            'extra_amount',
            'status',
            'reference_code',
            'created_at',
            'updated_at'
        ]


    def get_remaining_amount(self, obj):
        remaining = obj.expected_amount - obj.received_amount
        return float(max(remaining, 0))


    def get_payment_completed(self, obj):
        return obj.status == PaymentOrder.Status.COMPLETED
    def get_remaining_amount(self, obj):
        remaining = obj.expected_amount - obj.received_amount
        return float(max(remaining, 0))