import logging
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from chat.models.generation_history import GeneratedImage
from chat.serializers.generation_history_serializer import ImageHistorySerializer

logger = logging.getLogger(__name__)


class ImagesOnlyHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            qs = (
                GeneratedImage.objects.filter(post__session__user=request.user)
                .select_related("post__session")
                .order_by("-created_at")
            )

            data = ImageHistorySerializer(qs, many=True).data
            return Response({"images": data})
        except Exception as e:
            logger.error(f"Error fetching images history for user {request.user.id}: {str(e)}", exc_info=True)
            return Response(
                {"error": "Failed to fetch images history", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
