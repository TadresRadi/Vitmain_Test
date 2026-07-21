"""
Chat service — handles conversational AI replies via OpenAI.
"""
import logging
import os

from django.contrib.auth import get_user_model
from openai import OpenAI

from chat.models import AIChatSession, AIChatMessage
from chat.services.parsing import get_language_instruction
from onboarding.models import OnboardingResponse


User = get_user_model()
logger = logging.getLogger(__name__)

DEFAULT_OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

FALLBACK_REPLY = (
    "I'm sorry, I'm having trouble connecting to my creative mind "
    "right now. How else can I assist you with your marketing?"
)

def get_openai_client():
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

def _build_onboarding_context(user) -> str:
    try:
        onboarding = OnboardingResponse.objects.get(user=user)
    except OnboardingResponse.DoesNotExist:
        return ""

    marketing_goals = onboarding.marketing_goals if onboarding else []
    if isinstance(marketing_goals, list) and marketing_goals:
        marketing_goal = ", ".join(marketing_goals)
    else:
        marketing_goal = "a marketing campaign"

    tone_of_voice = onboarding.tone_of_voice if onboarding else "positive and premium"

    return f"""
Brand Context:
- Business Name: {onboarding.business_name}
- Industry/Type: {onboarding.business_type}
- Target Audience: {onboarding.target_audience}
- Marketing Goals: {marketing_goal}
- Tone of Voice: {tone_of_voice}
"""

def _format_chat_history(session: AIChatSession, limit: int = 15) -> str:
    history_msgs = session.messages.order_by('-created_at')[:limit]
    history_msgs = reversed(list(history_msgs))
    lines = []
    for m in history_msgs:
        sender_label = "User" if m.sender == 'user' else "Vitamin AI"
        lines.append(f"{sender_label}: {m.content}")
    return "\n".join(lines)

def _build_prompt(user, session: AIChatSession, content: str) -> str:
    onboarding_context = _build_onboarding_context(user)
    chat_history = _format_chat_history(session)
    lang_instruction = get_language_instruction(user.language or 'en')

    return f"""
You are a senior social media marketing copywriter and strategist. You are chatting with the user to help them refine their campaigns, brainstorm ideas, write captions, or analyze strategies.

{onboarding_context}

Here is the conversation history:
{chat_history}

Please generate a helpful, engaging, and professional response in {lang_instruction}. Keep it relevant to their marketing campaigns.
"""

def _call_openai(prompt: str) -> str:
    client = get_openai_client()
    if not client:
        logger.warning("OPENAI_API_KEY is not set; returning fallback chat reply")
        return FALLBACK_REPLY

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=DEFAULT_OPENAI_MODEL,
        )
        return chat_completion.choices[0].message.content
    except Exception:
        logger.exception("OpenAI chat error (model=%s)", DEFAULT_OPENAI_MODEL)
        return FALLBACK_REPLY

def generate_chat_reply(user, content: str) -> AIChatMessage:
    session, _ = AIChatSession.objects.get_or_create(user=user)
    AIChatMessage.objects.create(session=session, sender='user', content=content)
    prompt = _build_prompt(user, session, content)
    ai_reply = _call_openai(prompt)
    ai_msg = AIChatMessage.objects.create(
        session=session,
        sender='ai',
        content=ai_reply,
    )
    return ai_msg