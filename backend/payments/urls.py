from django.urls import path
from .views.create_payment_order_view import CreatePaymentOrderView
from .views.vodafone_cash_webhook_view import VodafoneCashWebhookView
from .views.order_status_view import OrderStatusView

app_name = 'payments'

urlpatterns = [
    path('create-order/', CreatePaymentOrderView.as_view(), name='create_order'),
    path('order-status/<uuid:pk>/', OrderStatusView.as_view(), name='order_status'),
     path('vodafone-cash/webhook/', VodafoneCashWebhookView.as_view(), name='vodafone_cash_webhook'),
]