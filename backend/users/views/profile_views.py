from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from core.utils import log_user_activity
from users.serializers import CustomUserSerializer

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = CustomUserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        log_user_activity(user, 'update_profile', {'fields': list(request.data.keys())})
        return Response(serializer.data)
