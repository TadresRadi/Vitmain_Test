from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from core.utils import log_user_activity
from support.models import SupportChat, SupportMessage
from support.serializers import SupportMessageSerializer

class AdminSupportChatReplyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.role not in ['super_admin', 'supervisor']:
            return Response({"error": "Access denied. Admin or supervisor privileges required."}, status=status.HTTP_403_FORBIDDEN)

        chat_id = request.data.get('chat_id')
        content = request.data.get('content')
        if not chat_id or not content:
            return Response({"error": "chat_id and content are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            chat = SupportChat.objects.get(id=chat_id)
        except SupportChat.DoesNotExist:
            return Response({"error": "Support chat not found."}, status=status.HTTP_404_NOT_FOUND)

        message = SupportMessage.objects.create(
            chat=chat,
            sender=request.user,
            content=content
        )
        
        log_user_activity(request.user, 'admin_reply_support', {
            'chat_id': str(chat.id),
            'reply_to': chat.user.email,
            'content_preview': content[:50]
        })

        return Response(SupportMessageSerializer(message).data, status=status.HTTP_201_CREATED)
