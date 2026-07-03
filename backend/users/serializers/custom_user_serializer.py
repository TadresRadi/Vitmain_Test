from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'phone_number', 'dob', 'user_type', 'role', 'language', 'date_joined']
        read_only_fields = ['id', 'role', 'date_joined']
