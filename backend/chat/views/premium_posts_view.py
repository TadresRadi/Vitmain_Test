import logging

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils import log_user_activity
from onboarding.models import OnboardingResponse
from subscriptions.permissions import HasActiveChatSubscription
from chat.models import AIChatMessage
from chat.serializers import AIChatSessionSerializer, AIPostGenerationSerializer
from chat.services.ai_posts import (
    generate_posts_from_onboarding,
    persist_post_generation,
    seed_onboarding_chat_session,
)

logger = logging.getLogger(__name__)


def _get_active_onboarding(user):
    onboarding = OnboardingResponse.objects.filter(user=user, is_active=True).first()
    if not onboarding:
        onboarding = OnboardingResponse.objects.filter(user=user).order_by("-created_at").first()
    return onboarding


class PremiumPostsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Return existing posts for any authenticated user who completed onboarding."""
        onboarding = _get_active_onboarding(request.user)
        if not onboarding:
            return Response(
                {"error": "Please complete the onboarding questionnaire first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session = seed_onboarding_chat_session(request.user, onboarding)
        post_gen = request.user.post_generations.order_by("-created_at").first()

        return Response({
            "session": AIChatSessionSerializer(session).data,
            "post_generation": AIPostGenerationSerializer(post_gen).data if post_gen else None,
        })

    def post(self, request):
        # Check subscription — can't use permission_classes because GET
        # doesn't require a subscription, only POST does.
        self.permission_classes = [permissions.IsAuthenticated, HasActiveChatSubscription]
        self.check_permissions(request)

        onboarding = _get_active_onboarding(request.user)
        if not onboarding:
            return Response(
                        {
            "error": "onboarding_required",
            "message": "Please complete onboarding first."
        },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if this is a forced regeneration request
        force_regenerate = request.data.get('force_regenerate', False)

        # Prevent duplicate post generation - check if user already has active posts
        # Only skip this check if force_regenerate is True
        if not force_regenerate:
            existing_post_gen = request.user.post_generations.filter(
                posts_review_complete=False
            ).order_by("-created_at").first()
            
            if existing_post_gen:
                # Posts already exist in progress, return them instead of regenerating
                return Response({
                    "session": AIChatSessionSerializer(seed_onboarding_chat_session(request.user, onboarding)).data,
                    "post_generation": AIPostGenerationSerializer(existing_post_gen).data,
                    "posts": existing_post_gen.posts,
                    "message": "Posts already exist, returning existing data."
                })

            # Also check if user has completed posts and return those if they exist
            completed_post_gen = request.user.post_generations.filter(
                posts_review_complete=True
            ).order_by("-created_at").first()
            
            if completed_post_gen:
                # User already has completed posts, return them
                return Response({
                    "session": AIChatSessionSerializer(seed_onboarding_chat_session(request.user, onboarding)).data,
                    "post_generation": AIPostGenerationSerializer(completed_post_gen).data,
                    "posts": completed_post_gen.posts,
                    "message": "Posts already exist, returning existing data."
                })

        session = seed_onboarding_chat_session(request.user, onboarding)
        user_lang = request.user.language or "en"
        posts, used_ai, ai_error = generate_posts_from_onboarding(onboarding, user_lang)

        if not used_ai:
            logger.warning(
                "Premium posts generation unavailable for user_id=%s: %s",
                request.user.id,
                ai_error,
            )
            return Response(
                {"error": "AI post generation is currently unavailable. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        post_gen = persist_post_generation(request.user, posts)

        # Update user status to indicate posts have been generated
        request.user.posts_generated = True
        request.user.save(update_fields=['posts_generated'])

        AIChatMessage.objects.create(
            session=session,
            sender="system",
            content="postReview.modifyPrompt",
        )

        log_user_activity(
            request.user,
            "generate_marketing_posts",
            {"post_generation_id": str(post_gen.id), "ai_generated": used_ai, "force_regenerate": force_regenerate},
        )

        return Response({
            "session": AIChatSessionSerializer(session).data,
            "post_generation": AIPostGenerationSerializer(post_gen).data,
            "posts": posts,
            "ai_generated": used_ai,
            "ai_error": ai_error,
        })
