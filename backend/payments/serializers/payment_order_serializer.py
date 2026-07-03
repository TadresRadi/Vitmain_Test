from rest_framework import serializers
from ..models.payment_order import PaymentOrder

class PaymentOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentOrder
        fields = [
            'id', 'user', 'plan', 'expected_amount', 
            'expected_sender_number', 'received_amount', 
            'status', 'reference_code', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'expected_amount', 'received_amount', 'status', 'reference_code', 'created_at', 'updated_at']