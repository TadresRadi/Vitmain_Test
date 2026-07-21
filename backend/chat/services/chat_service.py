"""
Chat service — handles conversational AI replies via Groq.

This module encapsulates the business logic for the chat feature:
building context from onboarding data, formatting chat history,
calling the Groq API, and persisting messages.
"""
import logging
import os

from django.contrib.auth import get_user_model

from chat.models import AIChatSession, AIChatMessage
from chat.services.ai_posts import get_groq_client
from chat.services.parsing import get_language_instruction
from onboarding.models import OnboardingResponse


User = get_user_model()
logger = logging.getLogger(__name__)

DEFAULT_GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

FALLBACK_REPLY = (
    "I'm sorry, I'm having trouble connecting to my creative mind "
    "right now. How else can I assist you with your marketing?"
)


def _build_onboarding_context(user) -> str:
    """
    Build brand context string from the user's onboarding response.

    Returns an empty string if the user has no onboarding response.
    """
    try:
        onboarding = OnboardingResponse.objects.get(user=user)
    except OnboardingResponse.DoesNotExist:
        return ""

    # Handle marketing_goals as array
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
    """
    Format recent chat messages into a string for the AI prompt.

    Fetches the last `limit` messages, reverses to chronological order,
    and formats each as "User: ..." or "Vitamin AI: ...".
    """
    history_msgs = session.messages.order_by('-created_at')[:limit]
    history_msgs = reversed(list(history_msgs))

    lines = []
    for m in history_msgs:
        sender_label = "User" if m.sender == 'user' else "Vitamin AI"
        lines.append(f"{sender_label}: {m.content}")
    return "\n".join(lines)


def _build_prompt(user, session: AIChatSession, content: str) -> str:
    """Build the full prompt for the Groq API."""
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


def _call_groq(prompt: str) -> str:
    """
    Call the Groq API and return the AI reply.

    Returns FALLBACK_REPLY if Groq is not configured or the API call fails.
    """
    client = get_groq_client()
    if not client:
        logger.warning("GROQ_API_KEY is not set; returning fallback chat reply")
        return FALLBACK_REPLY

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=DEFAULT_OPENAI_MODEL,
        )
        return chat_completion.choices[0].message.content
    except Exception:
        logger.exception(
            "Groq chat error (model=%s)",
            DEFAULT_GROQ_MODEL,
        )
        return FALLBACK_REPLY


def generate_chat_reply(user, content: str) -> AIChatMessage:
    """
    Process a user's chat message and generate an AI reply.

    This is the main entry point for the chat feature. It:
    1. Persists the user's message
    2. Builds context from onboarding + chat history
    3. Calls the Groq API (with fallback)
    4. Persists the AI's reply

    Args:
        user: The authenticated CustomUser instance.
        content: The user's message text.

    Returns:
        The AIChatMessage instance for the AI's reply.
    """
    # Get or create the user's chat session
    session, _ = AIChatSession.objects.get_or_create(user=user)

    # Persist the user's message
    AIChatMessage.objects.create(session=session, sender='user', content=content)

    # Build prompt and call Groq
    prompt = _build_prompt(user, session, content)
    ai_reply = _call_groq(prompt)

    # Persist the AI's reply
    ai_msg = AIChatMessage.objects.create(
        session=session,
        sender='ai',
        content=ai_reply,
    )

    return ai_msg