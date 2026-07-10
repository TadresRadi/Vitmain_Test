from django.conf import settings
from django.utils import timezone

from chat.models import (
    AIPostGeneration,
    AIChatSession,
    AIChatMessage,
)
from chat.models.generation_history import (
    GenerationSession,
    GeneratedPost,
    GeneratedImage,
)
from onboarding.models import OnboardingResponse
from chat.services.image_prompt_builder import build_imagen4_prompt
from chat.services.pollinations_images import generate_pollinations_image_bytes
from core.utils import log_user_activity


def process_image_generation(user, post_gen: AIPostGeneration, request):
    """
    Executes the image generation workflow for a given AIPostGeneration.
    Returns (posts_with_images, error_response).
    If successful, error_response is None.
    """
    onboarding = (
        OnboardingResponse.objects
        .filter(user=user, is_active=True)
        .order_by("-created_at")
        .first()
    )

    if onboarding is None:
        onboarding = (
            OnboardingResponse.objects
            .filter(user=user)
            .order_by("-created_at")
            .first()
        )

    btype = onboarding.business_type.lower() if onboarding else "business"
    marketing_goals = onboarding.marketing_goals if onboarding else []

    if isinstance(marketing_goals, list) and marketing_goals:
        marketing_goal = ", ".join(marketing_goals)
    else:
        marketing_goal = "a marketing campaign"

    tone_of_voice = (
        onboarding.tone_of_voice
        if onboarding
        else "positive and premium"
    )

    business_context = {
        "business_name": (
            onboarding.business_name
            if onboarding
            else "the business"
        ),
        "business_type": btype,
        "target_audience": (
            onboarding.target_audience
            if onboarding
            else "customers"
        ),
        "marketing_goals": marketing_goals,
        "marketing_goal": marketing_goal,
        "tone_of_voice": tone_of_voice,
    }

    posts_with_images = []

    for i, post in enumerate(post_gen.posts):
        prompt = build_imagen4_prompt(
            business=business_context,
            post_text=post,
        )

        try:
            image_bytes = generate_pollinations_image_bytes(
                prompt=prompt,
                model="flux",
            )

            rel_dir = f"generated_images/{user.id}/{post_gen.id}"
            abs_dir = settings.MEDIA_ROOT / rel_dir
            abs_dir.mkdir(parents=True, exist_ok=True)

            out_path = abs_dir / f"{i}.jpg"

            with open(out_path, "wb") as f:
                f.write(image_bytes)

            image_url = request.build_absolute_uri(
                f"{settings.MEDIA_URL}{rel_dir}/{i}.jpg"
            )

        except Exception as exc:
            post_gen.images_status = "failed"
            post_gen.images_generation_completed_at = timezone.now()
            post_gen.save(
                update_fields=[
                    "images_status",
                    "images_generation_completed_at",
                ]
            )

            return None, {
                "error": "Image generation failed",
                "provider": "pollinations",
                "details": str(exc),
                "failed_post_index": i,
                "images_status": "failed",
            }

        posts_with_images.append(
            {
                "post_index": i,
                "text": post,
                "image_url": image_url,
            }
        )

    try:
        history_session = GenerationSession.objects.create(
            user=user,
            post_generation=post_gen,
        )

        for generated in posts_with_images:
            generated_post = GeneratedPost.objects.create(
                session=history_session,
                post_index=generated["post_index"],
                post_text=generated["text"],
            )

            GeneratedImage.objects.create(
                post=generated_post,
                image_url=generated["image_url"],
                image_path=(
                    f"generated_images/{user.id}/{post_gen.id}/"
                    f"{generated['post_index']}.jpg"
                ),
            )

    except Exception:
        post_gen.images_status = "failed"
        post_gen.images_generation_completed_at = timezone.now()
        post_gen.save(
            update_fields=[
                "images_status",
                "images_generation_completed_at",
            ]
        )

        return None, {
            "error": "Could not save generated image history.",
            "images_status": "failed",
        }

    first_generation = not post_gen.has_images

    post_gen.has_images = True
    post_gen.images_status = "completed"
    post_gen.images_generation_completed_at = timezone.now()
    post_gen.save(
        update_fields=[
            "has_images",
            "images_status",
            "images_generation_completed_at",])

    if first_generation:
        user.images_generated = True
        user.save(update_fields=["images_generated"])

        session, _ = AIChatSession.objects.get_or_create(user=user)
        AIChatMessage.objects.create(
            session=session,
            sender="user",
            content="chat.generateMatchingImages",)
        AIChatMessage.objects.create(
            session=session,
            sender="ai",
            content="chat.visualAssetsPrepared",)

        log_user_activity(
            user,
            "generate_marketing_images",
            {"post_generation_id": str(post_gen.id)},)
