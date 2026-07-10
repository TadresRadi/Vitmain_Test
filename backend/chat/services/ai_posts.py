"""
Shared Groq post generation used by onboarding completion and premium-posts.
"""
import logging
import os

from groq import Groq

from chat.models import AIChatSession, AIChatMessage, AIPostGeneration


logger = logging.getLogger(__name__)

GROQ_API_KEY_ENV = "GROQ_API_KEY"
DEFAULT_GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")


def get_groq_client():
    """Read API key from environment and return Groq client instance."""
    api_key = os.environ.get(GROQ_API_KEY_ENV, "").strip()
    if not api_key:
        return None
    return Groq(api_key=api_key)


def build_marketing_posts_prompt(onboarding, user_lang="en"):
    """Build the marketing posts prompt from onboarding answers."""
    from chat.views.utils import get_language_instruction
    lang_instruction = get_language_instruction(user_lang)
    
    # Build business type description with subtype
    business_type_desc = onboarding.business_type
    if onboarding.business_subtype:
        business_type_desc += f" - {onboarding.business_subtype}"
    if onboarding.business_type_other:
        business_type_desc += f" (Other: {onboarding.business_type_other})"
    
    # Build marketing goals description
    marketing_goals_desc = ", ".join(onboarding.marketing_goals) if onboarding.marketing_goals else onboarding.marketing_goals
    
    # Build target audience description
    target_audience_desc = onboarding.target_audience
    if onboarding.target_audience_other:
        target_audience_desc += f" (Other: {onboarding.target_audience_other})"
    
    # Build tone of voice description
    tone_of_voice_desc = onboarding.tone_of_voice
    if onboarding.tone_of_voice_other:
        tone_of_voice_desc += f" (Other: {onboarding.tone_of_voice_other})"
    
    # Build location context
    location_context = f"Location: {onboarding.governorate}" if onboarding.governorate else ""
    
    return f"""
You are a senior social media marketing copywriter and strategist.
Generate exactly 5 tailored, creative, engaging, and professional social media marketing posts (text-only) for my brand:
- Business Name: {onboarding.business_name}
- {location_context}
- Industry/Type: {business_type_desc}
- Target Audience: {target_audience_desc}
- Marketing Goals: {marketing_goals_desc}
- Tone of Voice: {tone_of_voice_desc}

Rules:
1. Write all posts using this language instruction: {lang_instruction}
2. The posts should be ready to publish, featuring compelling hooks, call-to-actions, and appropriate hashtags.
3. Do not Translate the Business Name: {onboarding.business_name} should be used as-is in the posts.
4. You must format your output EXACTLY as a raw JSON array of strings:
[
  "Post 1 text here",
  "Post 2 text here",
  ...
]
Do not return any markdown code blocks, backticks, or other text outside the JSON array.
"""


def generate_posts_from_onboarding(onboarding, user_lang="en"):
    """
    Generate exactly 5 posts using Groq when configured, otherwise fallbacks.

    Returns:
        tuple: (posts: list[str], used_ai: bool, error_message: str | None)
    """
    from chat.views.utils import parse_ai_posts
    client = get_groq_client()
    if not client:
        logger.warning(
            "%s is not set; cannot generate marketing posts for business=%s",
            GROQ_API_KEY_ENV,
            onboarding.business_name,
        )
        return _fallback_posts(onboarding), False, f"{GROQ_API_KEY_ENV} is not configured."

    prompt = build_marketing_posts_prompt(onboarding, user_lang)
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=DEFAULT_GROQ_MODEL,
        )
        response_text = chat_completion.choices[0].message.content
        posts = parse_ai_posts(response_text)
        if len(posts) != 5:
            error_message = f"AI returned {len(posts)} valid posts; expected exactly 5."
            logger.warning("%s onboarding_id=%s", error_message, onboarding.id)
            return [], False, error_message
        return posts[:5], True, None
    except Exception as exc:
        logger.exception(
            "Groq post generation failed (onboarding_id=%s, model=%s)",
            onboarding.id,
            DEFAULT_GROQ_MODEL,
        )
        return [], False, "AI post generation failed."



def persist_post_generation(user, posts):
    """Store generated posts and return the AIPostGeneration instance."""
    return AIPostGeneration.objects.create(
        user=user,
        posts=posts,
        edit_count=0,
        posts_review_complete=False,
    )


def seed_onboarding_chat_session(user, onboarding):
    """Mirror onboarding Q&A into the user's chat session (existing structure)."""
    session, created = AIChatSession.objects.get_or_create(user=user)
    if not created and session.messages.exists():
        return session

    # Build business type description with subtype
    business_type_answer = onboarding.business_type
    if onboarding.business_subtype:
        business_type_answer += f" - {onboarding.business_subtype}"
    if onboarding.business_type_other:
        business_type_answer += f" (Other: {onboarding.business_type_other})"
    
    # Build marketing goals description
    marketing_goals_answer = ", ".join(onboarding.marketing_goals) if onboarding.marketing_goals else "Not specified"
    
    # Build target audience description
    target_audience_answer = onboarding.target_audience
    if onboarding.target_audience_other:
        target_audience_answer += f" (Other: {onboarding.target_audience_other})"
    
    # Build tone of voice description
    tone_of_voice_answer = onboarding.tone_of_voice
    if onboarding.tone_of_voice_other:
        tone_of_voice_answer += f" (Other: {onboarding.tone_of_voice_other})"

    pairs = [
        ("chat.onboarding.new.businessName", onboarding.business_name),
        ("chat.onboarding.new.governorate", onboarding.governorate or "Not specified"),
        ("chat.onboarding.new.businessType", business_type_answer),
        ("chat.onboarding.new.marketingGoals", marketing_goals_answer),
        ("chat.onboarding.new.targetAudience", target_audience_answer),
        ("chat.onboarding.new.toneOfVoice", tone_of_voice_answer),
    ]
    for question_key, answer in pairs:
        AIChatMessage.objects.create(session=session, sender="user", content=question_key)
        AIChatMessage.objects.create(session=session, sender="ai", content=answer)
    return session
