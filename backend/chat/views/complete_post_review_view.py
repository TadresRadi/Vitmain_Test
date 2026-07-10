from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils import log_user_activity
from chat.models import AIChatSession, AIChatMessage, AIPostGeneration
from chat.serializers import AIPostGenerationSerializer
from subscriptions.permissions import HasActiveChatSubscription

class CompletePostReviewView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasActiveChatSubscription]

    def post(self, request):
        post_gen = AIPostGeneration.objects.filter(user=request.user).order_by('-created_at').first()

        post_gen = AIPostGeneration.objects.filter(user=request.user).order_by('-created_at').first()
        if not post_gen:
            return Response(
                {"error": "No posts found. Please generate posts first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if post_gen.has_images:
            return Response(
                {"error": "Images have already been generated for this campaign."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        post_gen.posts_review_complete = True
        post_gen.save(update_fields=['posts_review_complete'])

        session, _ = AIChatSession.objects.get_or_create(user=request.user)
        AIChatMessage.objects.create(
            session=session,
            sender='system',
            content="postReview.readyForImages",
        )

        log_user_activity(request.user, 'complete_post_review', {
            'post_generation_id': str(post_gen.id),
        })

        return Response({
            "post_generation": AIPostGenerationSerializer(post_gen).data,
        })
