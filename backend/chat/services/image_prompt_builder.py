from __future__ import annotations

from typing import Dict, Any


def _clean(s: str | None) -> str:
    if not s:
        return ""
    return str(s).strip()


def build_imagen4_prompt(*, business: Dict[str, Any], post_text: str) -> str:
    """Build a high-quality prompt for image generation using the actual post content.

    Notes:
    - Uses the post content as the primary prompt for image generation
    - Incorporates business context for style consistency
    """

    business_name = _clean(business.get("business_name")) or "the business"
    business_type = _clean(business.get("business_type")) or "a business"
    target_audience = _clean(business.get("target_audience")) or "customers"
    
    # Handle marketing_goals as array
    marketing_goals = business.get("marketing_goals", [])
    if isinstance(marketing_goals, list) and marketing_goals:
        marketing_goal = ", ".join(marketing_goals)
    else:
        marketing_goal = _clean(business.get("marketing_goal")) or "a marketing campaign"
    
    # Use tone_of_voice instead of image_style and mood_style
    tone_of_voice = _clean(business.get("tone_of_voice")) or "positive and premium"

    # Use the actual post content as the primary prompt
    post_content = _clean(post_text)

    # Build prompt using the post content as the main inspiration
    return (
        f"Create a cinematic, photorealistic marketing image for {business_name}. "
        f"Business type: {business_type}. Target audience: {target_audience}. "
        f"Marketing goals: {marketing_goal}. "
        f"Tone of voice: {tone_of_voice}. "
        f"Create a visual representation that matches this marketing post: {post_content}. "
        "No logos and no readable text. "
        "Use natural lighting, realistic materials and textures, shallow depth of field, "
        "high detail, professional commercial photography, sharp focus on the main subject. "
        "Aspect ratio should match the requested output format." 
    )

