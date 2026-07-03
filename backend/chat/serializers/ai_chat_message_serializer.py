from rest_framework import serializers
from chat.models import AIChatMessage

class AIChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIChatMessage
        fields = ['id', 'sender', 'content', 'created_at']
