from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.email_service import get_email_service
from users.services.email_verification_service import EmailVerificationService

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'full_name', 'phone_number', 'dob', 'user_type', 'password', 'password_confirm']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords do not match."})  # nosec B105 - user-facing message
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=password,
            full_name=validated_data.get('full_name'),
            phone_number=validated_data.get('phone_number'),
            dob=validated_data.get('dob'),
            user_type=validated_data.get('user_type', 'explorer'),
            role='user',
            is_email_verified=False,  # New users must verify
        )

        # Send verification email (best-effort — don't fail registration
        # if email service is down). Frontend will prompt user to check
        # their inbox and offer a resend link.
        try:
            request = self.context.get('request')
            frontend_url = (
                request.META.get('HTTP_ORIGIN')
                if request
                else 'http://localhost:5173'
            )
            EmailVerificationService.initiate_verification(user, frontend_url)
        except Exception:
            # Logged inside the service; registration still succeeds.
            pass

        return user