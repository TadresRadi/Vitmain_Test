import logging
import os

from groq import Groq
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from onboarding.models import OnboardingResponse
from chat.models import AIChatSession, AIChatMessage
from chat.serializers import AIChatMessageSerializer
from .utils import get_language_instruction

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")


class SendChatMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        content = request.data.get("content")
        if not content:
            return Response({"error": "content is required."}, status=status.HTTP_400_BAD_REQUEST)

        onboarding_context = ""
        try:
            onboarding = OnboardingResponse.objects.get(user=request.user)
            # Handle marketing_goals as array
            marketing_goals = onboarding.marketing_goals if onboarding else []
            if isinstance(marketing_goals, list) and marketing_goals:
                marketing_goal = ", ".join(marketing_goals)
            else:
                marketing_goal = "a marketing campaign"
            
            # Use tone_of_voice instead of mood_style
            tone_of_voice = onboarding.tone_of_voice if onboarding else "positive and premium"
            
            onboarding_context = f"""
Brand Context:
- Business Name: {onboarding.business_name}
- Industry/Type: {onboarding.business_type}
- Target Audience: {onboarding.target_audience}
- Marketing Goals: {marketing_goal}
- Tone of Voice: {tone_of_voice}
"""
        except OnboardingResponse.DoesNotExist:
            pass

        session, _ = AIChatSession.objects.get_or_create(user=request.user)

        AIChatMessage.objects.create(session=session, sender='user', content=content)

        history_msgs = session.messages.order_by('-created_at')[:15]
        history_msgs = reversed(list(history_msgs))
        
        chat_history_str = ""
        for m in history_msgs:
            sender_label = "User" if m.sender == 'user' else "Vitamin AI"
            chat_history_str += f"{sender_label}: {m.content}\n"

        lang_instruction = get_language_instruction(request.user.language or 'en')
        prompt = f"""
You are a senior social media marketing copywriter and strategist. You are chatting with the user to help them refine their campaigns, brainstorm ideas, write captions, or analyze strategies.

{onboarding_context}

Here is the conversation history:
{chat_history_str}

Please generate a helpful, engaging, and professional response in {lang_instruction}. Keep it relevant to their marketing campaigns.
"""
        ai_reply = "I'm sorry, I'm having trouble connecting to my creative mind right now. How else can I assist you with your marketing?"
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
                ai_reply = chat_completion.choices[0].message.content
            except Exception:
                logger.exception("Groq chat error (user_id=%s)", getattr(request.user, "id", None))


        ai_msg = AIChatMessage.objects.create(session=session, sender='ai', content=ai_reply)

        return Response(AIChatMessageSerializer(ai_msg).data)
