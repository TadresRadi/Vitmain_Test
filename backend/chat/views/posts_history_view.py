import logging
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from chat.models.generation_history import GeneratedPost
from chat.serializers.generation_history_serializer import PostHistorySerializer

logger = logging.getLogger(__name__)


class PostsHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            qs = (
                GeneratedPost.objects.filter(session__user=request.user)
                .select_related("session")
                .order_by("-created_at")
            )

            data = PostHistorySerializer(qs, many=True).data
            return Response({"posts": data})
        except Exception as e:
            logger.error(f"Error fetching posts history for user {request.user.id}: {str(e)}", exc_info=True)
            return Response(
                {"error": "Failed to fetch posts history", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
