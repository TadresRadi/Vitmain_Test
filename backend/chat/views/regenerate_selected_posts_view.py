"""
View to regenerate specific posts selected by the user.
"""
import logging
import os
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from openai import OpenAI

logger = logging.getLogger(__name__)
DEFAULT_OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

class RegenerateSelectedPostsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_generation_id):
        from chat.models import AIPostGeneration
        try:
            post_gen = AIPostGeneration.objects.get(id=post_generation_id, user=request.user)
        except AIPostGeneration.DoesNotExist:
            return Response({"error": "Post generation not found."}, status=status.HTTP_404_NOT_FOUND)

        indexes = request.data.get("indexes", [])
        if not indexes or not isinstance(indexes, list):
            return Response({"error": "indexes (list of integers) are required."}, status=status.HTTP_400_BAD_REQUEST)

        api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not api_key:
            return Response({"error": "OpenAI API key is not configured."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            client = OpenAI(api_key=api_key)
            for idx in indexes:
                try:
                    idx_int = int(idx)
                    if 0 <= idx_int < len(post_gen.posts):
                        original_post = post_gen.posts[idx_int]
                        prompt = f"""
                        You are an expert copywriter. Please rewrite and improve this marketing post:
                        "{original_post}"
                        Return ONLY the rewritten post text.
                        """
                        chat_completion = client.chat.completions.create(
                            messages=[{"role": "user", "content": prompt}],
                            model=DEFAULT_OPENAI_MODEL,
                        )
                        new_post = chat_completion.choices[0].message.content.strip()
                        post_gen.posts[idx_int] = new_post
                except (ValueError, IndexError):
                    continue
            
            post_gen.edit_count += 1
            post_gen.save()

            from chat.serializers import AIPostGenerationSerializer
            return Response(AIPostGenerationSerializer(post_gen).data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("OpenAI regeneration error (user_id=%s, indexes=%s)", request.user.id, indexes)
            return Response({"error": "Failed to regenerate posts."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)