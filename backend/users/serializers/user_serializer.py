"""
User serializers with comprehensive validation.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.validators import InputValidator, ValidatorError

User = get_user_model()


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer for user profile details."""
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'full_name', 'phone_number', 'dob',
            'user_type', 'role', 'language', 'auth_provider',
            'profile_picture', 'onboarding_completed', 'date_joined', 'last_login'
        )
        read_only_fields = ('id', 'auth_provider', 'date_joined', 'last_login')
    
    def validate_email(self, value):
        """Validate email format."""
        try:
            InputValidator.validate_email(value)
        except ValidatorError as e:
            raise serializers.ValidationError(str(e))
        return value
    
    def validate_full_name(self, value):
        """Validate full name."""
        if value:
            try:
                InputValidator.validate_full_name(value)
            except ValidatorError as e:
                raise serializers.ValidationError(str(e))
        return value
    
    def validate_phone_number(self, value):
        """Validate phone number."""
        if value:
            try:
                InputValidator.validate_phone(value)
            except ValidatorError as e:
                raise serializers.ValidationError(str(e))
        return value


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile with validation."""
    
    class Meta:
        model = User
        fields = ('full_name', 'phone_number', 'dob', 'language', 'user_type')
    
    def validate_full_name(self, value):
        """Validate full name."""
        if value:
            try:
                InputValidator.validate_full_name(value)
            except ValidatorError as e:
                raise serializers.ValidationError(str(e))
        return value
    
    def validate_phone_number(self, value):
        """Validate phone number."""
        if value:
            try:
                InputValidator.validate_phone(value)
            except ValidatorError as e:
                raise serializers.ValidationError(str(e))
        return value
    
    def validate_language(self, value):
        """Validate language code."""
        allowed_languages = ['en', 'ar', 'fr', 'es']  # Update as needed
        try:
            InputValidator.validate_enum(value, allowed_languages)
        except ValidatorError as e:
            raise serializers.ValidationError(str(e))
        return value
    
    def validate_user_type(self, value):
        """Validate user type."""
        allowed_types = ['business_owner', 'explorer']
        try:
            InputValidator.validate_enum(value, allowed_types)
        except ValidatorError as e:
            raise serializers.ValidationError(str(e))
        return value


class GoogleAuthCallbackSerializer(serializers.Serializer):
    """Serializer for Google OAuth callback with validation."""
    
    id_token = serializers.CharField(required=False, allow_blank=True)
    access_token = serializers.CharField(required=False, allow_blank=True)
    state = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """Validate callback data."""
        id_token = data.get('id_token') or data.get('access_token')
        if not id_token:
            raise serializers.ValidationError(
                "Either 'id_token' or 'access_token' is required"
            )
        
        if len(id_token) > 10000:
            raise serializers.ValidationError("Token too long")
        
        data['token'] = id_token
        return data