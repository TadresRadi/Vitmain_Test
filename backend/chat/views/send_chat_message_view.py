"""
Chat message view — sends a user message and returns the AI reply.
"""
import logging

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.serializers import AIChatMessageSerializer
from chat.services import generate_chat_reply

logger = logging.getLogger(__name__)


class SendChatMessageView(APIView):
    """POST /api/chat/send — send a message and get an AI reply."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        content = request.data.get("content")
        if not content:
            return Response(
                {"error": "content is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ai_msg = generate_chat_reply(request.user, content)
        return Response(AIChatMessageSerializer(ai_msg).data)