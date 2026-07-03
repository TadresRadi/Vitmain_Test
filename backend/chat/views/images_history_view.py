from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models.generation_history import GenerationSession
from chat.serializers.generation_history_serializer import GenerationSessionSerializer


class ImagesHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = (
            GenerationSession.objects.filter(user=request.user)
            .select_related("post_generation")
            .prefetch_related("posts__images")
            .order_by("-created_at")
        )

        # DRF nested serializers will include posts ordered by post_index (model Meta ordering).
        data = GenerationSessionSerializer(qs, many=True).data
        return Response({"sessions": data})
