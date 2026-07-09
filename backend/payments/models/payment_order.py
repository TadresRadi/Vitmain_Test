from django.db import models
from django.conf import settings
import uuid

class PaymentOrder(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PARTIAL = 'partial', 'Partial'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_orders')
    plan = models.CharField(max_length=100)
    expected_amount = models.DecimalField(max_digits=10, decimal_places=2) # Configured ONLY in backend
    expected_sender_number = models.CharField(max_length=20, db_index=True) # User's declared phone
    extra_amount=models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    received_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    reference_code = models.CharField(max_length=20, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.reference_code} - Expected: {self.expected_amount} EGP"