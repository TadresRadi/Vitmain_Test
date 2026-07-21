import logging
import os

from groq import Groq
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils import log_user_activity
from onboarding.models import OnboardingResponse
from subscriptions.permissions import HasActiveChatSubscription
from chat.models import AIChatMessage, AIChatSession, AIPostGeneration
from chat.serializers import AIPostGenerationSerializer
from chat.services.parsing import get_language_instruction, parse_ai_post_text
logger = logging.getLogger(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")


def _get_active_onboarding(user):
    onboarding = OnboardingResponse.objects.filter(user=user, is_active=True).first()
    if not onboarding:
        onboarding = OnboardingResponse.objects.filter(user=user).order_by("-created_at").first()
    return onboarding


def _build_regeneration_prompt(onboarding, current_posts, post_index, language):
    marketing_goals = onboarding.marketing_goals if onboarding else []
    marketing_goal = (
        ", ".join(marketing_goals)
        if isinstance(marketing_goals, list) and marketing_goals
        else "a marketing campaign"
    )
    tone_of_voice = onboarding.tone_of_voice if onboarding else "positive and premium"

    return f"""
You are a senior social media marketing copywriter.

Regenerate exactly one post for a five-post content plan. Preserve the brand language and write the result in {language}.

Brand context:
- Business name: {onboarding.business_name}
- Business type: {onboarding.business_type}
- Extra business details: {onboarding.business_type_other or "None"}
- Target audience: {onboarding.target_audience}
- Marketing goals: {marketing_goal}
- Tone of voice: {tone_of_voice}

Existing posts:
{current_posts}

Task:
- Regenerate post number {post_index + 1}.
- Make it clearly different from the current post and from the other posts.
- Include a suitable CTA and relevant hashtags.
- Keep the content ready to publish.

Return a JSON string only, with no markdown and no text outside the string:
"Post text here"
"""


class RegenerateSelectedPostsView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasActiveChatSubscription]

    def post(self, request):
        onboarding = _get_active_onboarding(request.user)

        onboarding = _get_active_onboarding(request.user)
        if not onboarding:
            return Response(
                {"error": "Please complete the onboarding questionnaire first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        selected_indexes = request.data.get("selected_indexes", [])
        if not selected_indexes or not isinstance(selected_indexes, list):
            return Response(
                {"error": "selected_indexes is required and must be a list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        post_gen = AIPostGeneration.objects.filter(user=request.user).order_by("-created_at").first()
        if not post_gen:
            return Response(
                {"error": "No posts found to regenerate. Please generate posts first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        current_posts = list(post_gen.posts)
        if len(current_posts) != 5:
            return Response({"error": "Expected 5 posts to regenerate."}, status=status.HTTP_400_BAD_REQUEST)

        for index in selected_indexes:
            if not isinstance(index, int) or index < 0 or index >= len(current_posts):
                return Response(
                    {"error": f"Invalid post index: {index}. Indexes must be between 0 and 4."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if not GROQ_API_KEY:
            return Response(
                {"error": "AI post regeneration is currently unavailable. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        regenerated_posts = current_posts.copy()
        language = get_language_instruction(request.user.language or "en")

        try:
            client = Groq(api_key=GROQ_API_KEY)
            for index in selected_indexes:
                prompt = _build_regeneration_prompt(onboarding, current_posts, index, language)
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=DEFAULT_OPENAI_MODEL,
                )
                new_post = parse_ai_post_text(completion.choices[0].message.content)
                if not new_post:
                    return Response(
                        {"error": "AI returned an empty regenerated post."},
                        status=status.HTTP_502_BAD_GATEWAY,
                    )
                regenerated_posts[index] = new_post
        except Exception:
            logger.exception(
                "Groq regeneration error (user_id=%s, indexes=%s)",
                getattr(request.user, "id", None),
                selected_indexes,
            )
            return Response(
                {"error": "Failed to regenerate selected posts."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        session, _ = AIChatSession.objects.get_or_create(user=request.user)

        post_gen.posts = regenerated_posts
        post_gen.edit_count += 1
        post_gen.posts_review_complete = True
        post_gen.save(update_fields=["posts", "edit_count", "posts_review_complete"])

        AIChatMessage.objects.create(
            session=session,
            sender="system",
            content="postReview.postsUpdated",
        )
        AIChatMessage.objects.create(
            session=session,
            sender="system",
            content="postReview.readyForImages",
        )

        log_user_activity(
            request.user,
            "regenerate_selected_posts",
            {
                "post_generation_id": str(post_gen.id),
                "selected_indexes": selected_indexes,
                "edit_count": post_gen.edit_count,
            },
        )

        return Response(
            {
                "posts": regenerated_posts,
                "post_generation": AIPostGenerationSerializer(post_gen).data,
            }
        )
