from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from core.utils import log_user_activity

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Prevent supervisor and admin accounts from logging in through user login
        if self.user.role in ['supervisor', 'super_admin']:
            raise serializers.ValidationError(
                "Admin and supervisor accounts must use the admin login portal. "
                "Please use the admin login page to access your account."
            )
        
        data['user'] = {
            'id': str(self.user.id),
            'email': self.user.email,
            'role': self.user.role,
            'full_name': self.user.full_name,
            'onboarding_completed': self.user.onboarding_completed
        }
        data['access_token'] = data['access']  # Frontend compatibility
        log_user_activity(self.user, 'login', {'ip': self.context.get('request').META.get('REMOTE_ADDR')})
        return data
