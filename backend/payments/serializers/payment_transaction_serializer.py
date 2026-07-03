from rest_framework import serializers
from ..models.payment_transaction import PaymentTransaction

class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = ['id', 'order', 'amount', 'sender_number', 'raw_sms', 'created_at']