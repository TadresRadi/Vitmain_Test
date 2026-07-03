from rest_framework import serializers
from .models import Project, SuccessStory, SuccessStorySettings, FeaturedProject, Brand, TeslaClientImage


class ProjectSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'category', 'image', 'image_url', 'order', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class SuccessStorySerializer(serializers.ModelSerializer):
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = SuccessStory
        fields = ['id', 'content_en', 'content_ar', 'video', 'video_url', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_video_url(self, obj):
        if obj.video:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.video.url)
            return obj.video.url
        return None


class SuccessStorySettingsSerializer(serializers.ModelSerializer):
    featured_video_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    featured_video_details = serializers.SerializerMethodField()

    class Meta:
        model = SuccessStorySettings
        fields = ['id', 'mode', 'rotation_interval', 'featured_video', 'featured_video_id', 'featured_video_details', 'updated_at']
        read_only_fields = ['updated_at']

    def get_featured_video_details(self, obj):
        if obj.featured_video:
            return {
                'id': obj.featured_video.id,
                'content_en': obj.featured_video.content_en,
                'video_url': obj.featured_video.video.url if obj.featured_video.video else None
            }
        return None

    def update(self, instance, validated_data):
        featured_video_id = validated_data.pop('featured_video_id', None)
        if featured_video_id is not None:
            if featured_video_id == 0 or featured_video_id == '':
                instance.featured_video = None
            else:
                try:
                    instance.featured_video = SuccessStory.objects.get(id=featured_video_id)
                except SuccessStory.DoesNotExist:
                    instance.featured_video = None
        return super().update(instance, validated_data)


class FeaturedProjectSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = FeaturedProject
        fields = ['id', 'title', 'description', 'category', 'image', 'image_url', 'order', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def validate(self, data):
        # Check if creating a new featured project would exceed the limit of 6
        if self.instance is None:  # Creating new
            current_count = FeaturedProject.objects.count()
            if current_count >= 6:
                raise serializers.ValidationError("Maximum of 6 featured projects allowed.")
        return data


class BrandSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ['id', 'name', 'logo', 'logo_url', 'order', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_logo_url(self, obj):
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None


class TeslaClientImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = TeslaClientImage
        fields = ['id', 'title', 'image', 'image_url', 'order', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
