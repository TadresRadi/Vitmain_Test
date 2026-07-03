from rest_framework import serializers
from support.models import SupportChat
from .support_message_serializer import SupportMessageSerializer

class SupportChatSerializer(serializers.ModelSerializer):
    messages = SupportMessageSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_phone = serializers.CharField(source='user.phone_number', read_only=True)

    class Meta:
        model = SupportChat
        fields = ['id', 'user', 'user_email', 'user_name', 'user_phone', 'created_at', 'messages']
