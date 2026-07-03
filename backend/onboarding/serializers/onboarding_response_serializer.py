from rest_framework import serializers
from onboarding.models import OnboardingResponse

class OnboardingResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnboardingResponse
        fields = [
            'business_name',
            'governorate',
            'business_type',
            'business_subtype',
            'business_type_other',
            'marketing_goals',
            'target_audience',
            'target_audience_other',
            'tone_of_voice',
            'tone_of_voice_other',
            'created_at'
        ]
        read_only_fields = ['created_at']
