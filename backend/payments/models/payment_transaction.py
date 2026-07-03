from django.db import models
from .payment_order import PaymentOrder

class PaymentTransaction(models.Model):
    id = models.CharField(max_length=100, primary_key=True) # Vodafone Transaction ID
    order = models.ForeignKey(PaymentOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    sender_number = models.CharField(max_length=20)
    raw_sms = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment_transactions'
        ordering = ['-created_at']