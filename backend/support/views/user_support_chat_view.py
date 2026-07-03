from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from core.utils import log_user_activity
from support.models import SupportChat, SupportMessage
from support.serializers import SupportChatSerializer, SupportMessageSerializer
from .utils import get_support_admin

class UserSupportChatView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        chat, created = SupportChat.objects.get_or_create(user=request.user)
        
        if created or chat.messages.count() == 0:
            support_admin = get_support_admin()
            SupportMessage.objects.create(
                chat=chat,
                sender=support_admin,
                content="Welcome! How can we help you today?"
            )
            log_user_activity(request.user, 'start_support_chat', {'chat_id': str(chat.id)})

        serializer = SupportChatSerializer(chat)
        return Response(serializer.data)

    def post(self, request):
        chat, _ = SupportChat.objects.get_or_create(user=request.user)
        content = request.data.get('content')
        if not content:
            return Response({"error": "content is required."}, status=status.HTTP_400_BAD_REQUEST)

        message = SupportMessage.objects.create(
            chat=chat,
            sender=request.user,
            content=content
        )
        log_user_activity(request.user, 'send_support_message', {
            'chat_id': str(chat.id),
            'content_preview': content[:50]
        })
        
        return Response(SupportMessageSerializer(message).data, status=status.HTTP_201_CREATED)
