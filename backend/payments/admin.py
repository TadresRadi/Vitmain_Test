from django.contrib import admin
from .models import PaymentOrder, PaymentTransaction

@admin.register(PaymentOrder)
class PaymentOrderAdmin(admin.ModelAdmin):
    list_display = ['reference_code', 'user', 'expected_amount', 'received_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['reference_code', 'user__email']

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'amount', 'sender_number', 'created_at']
    list_filter = ['created_at']
    search_fields = ['id', 'sender_number']