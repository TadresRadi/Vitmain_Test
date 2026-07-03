from rest_framework import status, permissions, generics
from rest_framework.response import Response
from core.utils import log_user_activity
from users.serializers import CustomUserSerializer, RegisterSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        log_user_activity(user, 'register', {
            'user_type': user.user_type,
            'phone_number': user.phone_number,
            'dob': str(user.dob) if user.dob else None
        })
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "User registered successfully.", "user": CustomUserSerializer(user).data},
            status=status.HTTP_201_CREATED,
            headers=headers
        )
