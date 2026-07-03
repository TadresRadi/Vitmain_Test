from rest_framework import serializers
from support.models import SupportMessage

class SupportMessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.CharField(source='sender.email', read_only=True)
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)

    class Meta:
        model = SupportMessage
        fields = ['id', 'sender', 'sender_email', 'sender_name', 'content', 'created_at']
