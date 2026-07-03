from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from support.models import SupportChat
from support.serializers import SupportChatSerializer

class AdminSupportChatListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role not in ['super_admin', 'supervisor']:
            return Response({"error": "Access denied. Admin or supervisor privileges required."}, status=status.HTTP_403_FORBIDDEN)

        chats = SupportChat.objects.all().order_by('-created_at')
        serializer = SupportChatSerializer(chats, many=True)
        return Response(serializer.data)
