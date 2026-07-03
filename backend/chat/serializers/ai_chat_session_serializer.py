from rest_framework import serializers
from chat.models import AIChatSession
from .ai_chat_message_serializer import AIChatMessageSerializer

class AIChatSessionSerializer(serializers.ModelSerializer):
    messages = AIChatMessageSerializer(many=True, read_only=True)
    class Meta:
        model = AIChatSession
        fields = ['id', 'created_at', 'messages']
