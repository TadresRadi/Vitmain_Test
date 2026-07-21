"""
View to modify a specific post using AI.
"""
import logging
import os
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from openai import OpenAI

logger = logging.getLogger(__name__)
DEFAULT_OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

class ModifyPostsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_generation_id):
        from chat.models import AIPostGeneration
        try:
            post_gen = AIPostGeneration.objects.get(id=post_generation_id, user=request.user)
        except AIPostGeneration.DoesNotExist:
            return Response({"error": "Post generation not found."}, status=status.HTTP_404_NOT_FOUND)

        post_index = request.data.get("post_index")
        modification_request = request.data.get("modification_request")

        if post_index is None or modification_request is None:
            return Response({"error": "post_index and modification_request are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            post_index = int(post_index)
            if post_index < 0 or post_index >= len(post_gen.posts):
                return Response({"error": "Invalid post index."}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "post_index must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        original_post = post_gen.posts[post_index]
        
        api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        if api_key:
            try:
                client = OpenAI(api_key=api_key)
                prompt = f"""
                You are an expert copywriter. A user wants to modify one of their marketing posts.
                Original Post: "{original_post}"
                User Request: "{modification_request}"
                Please provide the modified post. Return ONLY the modified post text, no explanations.
                """
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=DEFAULT_OPENAI_MODEL,
                )
                modified_post = chat_completion.choices[0].message.content.strip()
                
                post_gen.posts[post_index] = modified_post
                post_gen.edit_count += 1
                post_gen.save()

                from chat.serializers import AIPostGenerationSerializer
                return Response(AIPostGenerationSerializer(post_gen).data, status=status.HTTP_200_OK)
            except Exception as e:
                logger.exception("OpenAI modification error (user_id=%s, post_generation_id=%s)", request.user.id, post_generation_id)
                return Response({"error": "Failed to modify post."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"error": "OpenAI API key is not configured."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)