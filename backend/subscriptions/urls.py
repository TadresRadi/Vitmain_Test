from django.urls import path
from subscriptions.views import PlanListView, SubscribeView, SubscriptionStatusView

urlpatterns = [
    path('plans', PlanListView.as_view(), name='plans_list'),
    path('subscription/subscribe', SubscribeView.as_view(), name='subscribe_plan'),
    path('subscription/status', SubscriptionStatusView.as_view(), name='subscription_status'),
]
