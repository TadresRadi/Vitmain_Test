from rest_framework import serializers
from subscriptions.models import Subscription
from .plan_serializer import PlanSerializer

class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    class Meta:
        model = Subscription
        fields = ['id', 'active', 'started_at', 'expires_at', 'plan']
