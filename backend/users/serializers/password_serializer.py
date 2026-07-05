"""
Password-related serializers.
"""
from rest_framework import serializers
from core.validators import InputValidator, ValidatorError


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    old_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate_old_password(self, value):
        """Validate old password is provided."""
        if not value:
            raise serializers.ValidationError("Current password is required")
        return value
    
    def validate_new_password(self, value):
        """Validate new password strength."""
        if not value:
            raise serializers.ValidationError("New password is required")
        
        try:
            InputValidator.validate_password(value)
        except ValidatorError as e:
            raise serializers.ValidationError(str(e))
        
        return value
    
    def validate_confirm_password(self, value):
        """Validate confirm password is provided."""
        if not value:
            raise serializers.ValidationError("Password confirmation is required")
        return value
    
    def validate(self, data):
        """Validate password change data."""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {'confirm_password': 'Passwords do not match'}
            )
        
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError(
                {'new_password': 'New password must be different from current password'}
            )
        
        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request."""
    
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Validate email."""
        try:
            InputValidator.validate_email(value)
        except ValidatorError as e:
            raise serializers.ValidationError(str(e))
        return value.lower()


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset."""
    
    email = serializers.EmailField(required=True)
    token = serializers.CharField(required=True, max_length=1000)
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate_email(self, value):
        """Validate email."""
        try:
            InputValidator.validate_email(value)
        except ValidatorError as e:
            raise serializers.ValidationError(str(e))
        return value.lower()
    
    def validate_token(self, value):
        """Validate token format."""
        if not value or len(value) < 10:
            raise serializers.ValidationError("Invalid reset token")
        return value
    
    def validate_new_password(self, value):
        """Validate new password strength."""
        try:
            InputValidator.validate_password(value)
        except ValidatorError as e:
            raise serializers.ValidationError(str(e))
        return value
    
    def validate(self, data):
        """Validate reset data."""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {'confirm_password': 'Passwords do not match'}
            )
        return data


class PasswordStrengthCheckSerializer(serializers.Serializer):
    """Serializer for password strength check."""
    
    password = serializers.CharField(required=True, write_only=True)
    
    def validate_password(self, value):
        """Validate password is provided."""
        if not value:
            raise serializers.ValidationError("Password is required")
        return value