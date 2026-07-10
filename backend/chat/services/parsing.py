"""
Parsing utilities for AI-generated content.

These functions are pure (no HTTP/DRF dependencies) and belong in the
service layer. They were previously in chat/views/utils.py, which created
an inverted dependency (services importing from views).
"""
import json
import re


def clean_json_response(text):
    """Strip markdown code fences from an AI response."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def parse_ai_posts(text):
    """
    Parse AI response into a list of up to 5 post strings.

    Tries JSON array first, falls back to line-by-line parsing.
    """
    cleaned = clean_json_response(text)
    try:
        data = json.loads(cleaned)
        if isinstance(data, list):
            return [str(item).strip() for item in data if str(item).strip()][:5]
    except Exception:
        pass

    lines = [line.strip() for line in re.split(r'\n+', text) if line.strip()]
    posts = []
    for line in lines:
        cleaned_line = re.sub(r'^(Post\s*\d+:?|\d+\.?)\s*', '', line, flags=re.IGNORECASE).strip()
        if len(cleaned_line) > 10:
            posts.append(cleaned_line)

    return posts[:5]


def parse_ai_post_text(text):
    """
    Parse a single AI-generated post from a JSON string response.

    Tries JSON string first, falls back to stripping quotes.
    """
    cleaned = clean_json_response(text)
    try:
        data = json.loads(cleaned)
        if isinstance(data, str) and data.strip():
            return data.strip()
    except Exception:
        pass
    return cleaned.strip().strip('"')


def get_language_instruction(user_lang):
    """
    Build the language instruction string for AI prompts.

    Returns Egyptian Arabic dialect instruction for Arabic,
    or a generic instruction for the given language code.
    """
    lang = (user_lang or "").strip().lower()
    if lang in ["ar", "arabic"]:
        return (
            "Egyptian Arabic dialect (Egyptian colloquial Arabic) rather than "
            "Modern Standard Arabic. The tone should feel natural and authentic "
            "to Egyptian audiences, using professional, engaging, marketing-focused "
            "wording with commonly understood Egyptian expressions."
        )
    return f"the '{user_lang}' language"