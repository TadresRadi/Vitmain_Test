import json
import logging
import os

from groq import Groq
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils import log_user_activity
from chat.models import AIChatSession, AIChatMessage, AIPostGeneration
from chat.serializers import AIPostGenerationSerializer
from chat.services.parsing import parse_ai_posts, get_language_instruction
logger = logging.getLogger(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")


class ModifyPostsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        post_gen_id = request.data.get("post_generation_id")
        modifications = request.data.get("modifications")

        if not post_gen_id or modifications is None:
            return Response(
                {"error": "post_generation_id and modifications are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(modifications, list):
            return Response(
                {"error": "modifications must be a list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            post_gen = AIPostGeneration.objects.get(id=post_gen_id, user=request.user)
        except AIPostGeneration.DoesNotExist:
            return Response({"error": "Post generation record not found."}, status=status.HTTP_404_NOT_FOUND)

        if post_gen.edit_count >= 1:
            return Response({"error": "Post modification is allowed only once. You have already modified these posts."}, status=status.HTTP_400_BAD_REQUEST)

        current_posts = list(post_gen.posts)
        user_lang = request.user.language or "en"

        mod_instructions = ""
        for mod in modifications:
            if not isinstance(mod, dict):
                continue

            post_index_raw = mod.get("post_index")
            inst = mod.get("instruction")

            if inst is None or not isinstance(inst, str):
                continue

            try:
                idx = int(post_index_raw)
            except (TypeError, ValueError):
                continue

            if 0 <= idx < len(current_posts):
                mod_instructions += f"- Post #{idx + 1} ('{current_posts[idx]}'): {inst}\n"

        lang_instruction = get_language_instruction(user_lang)
        prompt = f"""
You are a senior social media copywriter. I have some generated social media posts, and I want to edit them based on specific instructions.
Keep all other posts unchanged.

Here are the modification instructions:
{mod_instructions}

Return the complete updated list of 5 posts in {lang_instruction}.
You must format your output EXACTLY as a raw JSON array of strings:
[
  "Post 1 text here",
  "Post 2 text here",
  ...
]
Do not return any markdown code blocks, backticks, or other text outside the JSON array.
"""
        updated_posts = current_posts
        if GROQ_API_KEY:
            try:
                client = Groq(api_key=GROQ_API_KEY)
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model=GROQ_MODEL,
                )
                response_text = chat_completion.choices[0].message.content
                updated_posts = parse_ai_posts(response_text)
            except Exception:
                logger.exception(
                    "Groq modification error (user_id=%s, post_generation_id=%s)",
                    getattr(request.user, "id", None),
                    post_gen_id,
                )
                return Response(
                    {"error": "Failed to generate modified posts."},
                    status=status.HTTP_502_BAD_GATEWAY,
                )


        if not isinstance(updated_posts, list) or len(updated_posts) != len(current_posts):
            logger.error(
                "Invalid updated_posts from parse_ai_posts (user_id=%s, post_generation_id=%s)",
                getattr(request.user, "id", None),
                post_gen_id,
            )
            return Response(
                {"error": "Modified posts output was invalid."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        post_gen.posts = updated_posts
        post_gen.edit_count += 1
        post_gen.save()

        session, _ = AIChatSession.objects.get_or_create(user=request.user)
        AIChatMessage.objects.create(
            session=session,
            sender='user',
            content=f"Requesting post modifications: {json.dumps(modifications)}"
        )
        AIChatMessage.objects.create(
            session=session,
            sender='ai',
            content="Here are your modified posts. No further edits can be made."
        )

        log_user_activity(request.user, 'modify_marketing_posts', {
            'post_generation_id': str(post_gen.id),
            'modifications': modifications
        })

        return Response(AIPostGenerationSerializer(post_gen).data)
