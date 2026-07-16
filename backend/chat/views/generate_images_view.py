from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import timedelta

from django.utils import timezone
from chat.models import AIPostGeneration
from chat.serializers import AIPostGenerationSerializer
from subscriptions.permissions import HasActiveChatSubscription
from chat.services import process_image_generation
class GenerateImagesView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasActiveChatSubscription]

    def post(self, request):
        post_gen_id = request.data.get("post_generation_id")

        if not post_gen_id:
            return Response({"error": "post_generation_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            post_gen = AIPostGeneration.objects.get(id=post_gen_id, user=request.user)
        except AIPostGeneration.DoesNotExist:
            return Response({"error": "Post generation record not found."}, status=status.HTTP_404_NOT_FOUND)

        if post_gen.images_status == "processing":
            stale_before = timezone.now() - timedelta(minutes=10)

            if (
                post_gen.images_generation_started_at
                and post_gen.images_generation_started_at < stale_before):
                post_gen.images_status = "failed"
                post_gen.images_generation_completed_at = timezone.now()
                post_gen.save(update_fields=["images_status","images_generation_completed_at",])
            else:
                return Response({"error": ("Image generation is already in progress. ""Please wait for it to complete."),"images_status": "processing",},status=status.HTTP_409_CONFLICT,)

        if post_gen.has_images:
            existing_session = post_gen.generation_sessions.order_by("-created_at").first()
            if existing_session:
                existing_posts_with_images = []
                for gp in existing_session.posts.all().order_by("post_index"):
                    image = gp.images.first()
                    if image:
                        existing_posts_with_images.append({
                            "post_index": gp.post_index,
                            "text": gp.post_text,
                            "image_url": image.image_url,
                        })
                if existing_posts_with_images:
                    return Response({
                        "post_generation": AIPostGenerationSerializer(post_gen).data,
                        "posts_with_images": existing_posts_with_images,
                        "message": "Images already exist, returning existing data."
                    })

        if not post_gen.posts_review_complete and not post_gen.has_images:
            return Response(
                {"error": "Please review and confirm your posts before generating images."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        post_gen.images_status = 'processing'
        post_gen.images_generation_started_at = timezone.now()
        post_gen.save(update_fields=['images_status', 'images_generation_started_at'])

        base_url = request.build_absolute_uri("/")
        posts_with_images, error_response = process_image_generation(request.user, post_gen, base_url)
        if error_response:
            return Response(error_response, status=status.HTTP_502_BAD_GATEWAY)

        return Response(
            {
                "post_generation": AIPostGenerationSerializer(post_gen).data,
                "posts_with_images": posts_with_images,
            }
        )

