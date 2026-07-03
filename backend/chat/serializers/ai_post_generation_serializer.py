from rest_framework import serializers
from chat.models import AIPostGeneration

class AIPostGenerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIPostGeneration
        fields = [
            'id',
            'posts',
            'edit_count',
            'has_images',
            'posts_review_complete',
            'images_status',
            'images_generation_started_at',
            'images_generation_completed_at',
            'created_at'
        ]
