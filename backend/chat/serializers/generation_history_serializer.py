from rest_framework import serializers

from chat.models.generation_history import GenerationSession, GeneratedPost, GeneratedImage


class GeneratedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedImage
        fields = ["id", "image_url", "image_path", "created_at"]


class GeneratedPostSerializer(serializers.ModelSerializer):
    images = GeneratedImageSerializer(many=True, read_only=True)

    class Meta:
        model = GeneratedPost
        fields = ["id", "post_index", "post_text", "images", "created_at"]


class GenerationSessionSerializer(serializers.ModelSerializer):
    posts = GeneratedPostSerializer(many=True, read_only=True)

    class Meta:
        model = GenerationSession
        fields = ["id", "created_at", "posts"]


class ImagesHistoryResponseSerializer(serializers.Serializer):
    sessions = GenerationSessionSerializer(many=True)


class PostHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedPost
        fields = ["id", "post_index", "post_text", "created_at"]


class ImageHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedImage
        fields = ["id", "image_url", "image_path", "created_at"]
