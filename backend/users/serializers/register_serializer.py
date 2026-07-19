"""
Serializer for user registration.

Creates the user with is_email_verified=False, then triggers the
email verification flow. The user cannot log in until they click
the verification link.
"""
import logging
from rest_framework import serializers
from django.contrib.auth import get_user_model
from users.services.email_verification_service import EmailVerificationService

logger = logging.getLogger(__name__)
User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'full_name', 'phone_number', 'dob', 'user_type', 'password', 'password_confirm']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
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
            is_email_verified=False,
        )

        # Send verification email (best-effort — don't fail registration
        # if the email service is down). The frontend will prompt the user
        # to check their inbox and offer a resend link.
        try:
            request = self.context.get('request')
            frontend_url = (
                request.META.get('HTTP_ORIGIN')
                if request
                else 'http://localhost:5173'
            )

            logger.info("Sending verification email to %s (frontend_url=%s)", user.email, frontend_url)

            sent = EmailVerificationService.initiate_verification(user, frontend_url)

            if sent:
                logger.info("Verification email sent successfully to %s", user.email)
            else:
                logger.warning("Verification email could not be sent to %s (email service unavailable or token storage failed)", user.email)

        except Exception:
            logger.exception("Failed to send verification email during registration for %s", user.email)

        return user