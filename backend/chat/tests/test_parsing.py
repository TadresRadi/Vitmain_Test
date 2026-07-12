"""
Tests for AI response parsing utilities.

These are pure functions — no database access needed, so they run fast.

If Phase 3 Batch 5 was applied, the functions live in
chat/services/parsing.py. Otherwise, they're in chat/views/utils.py.
This test file tries the new location first, then falls back.

Run: pytest chat/tests/test_parsing.py -v
"""


# Try importing from the new location (Phase 3 Batch 5), fall back to old
try:
    from chat.services.parsing import (
        clean_json_response,
        parse_ai_posts,
        parse_ai_post_text,
        get_language_instruction,
    )
except ImportError:
    from chat.views.utils import (
        clean_json_response,
        parse_ai_posts,
        parse_ai_post_text,
        get_language_instruction,
    )


# ============================================================================
# clean_json_response
# ============================================================================

class TestCleanJsonResponse:
    def test_strips_leading_json_fence(self):
        assert clean_json_response("```json\n[\"a\"]\n```") == "[\"a\"]"

    def test_strips_plain_fence(self):
        assert clean_json_response("```\n[\"a\"]\n```") == "[\"a\"]"

    def test_strips_trailing_fence_only(self):
        assert clean_json_response("[\"a\"]\n```") == "[\"a\"]"

    def test_strips_whitespace(self):
        assert clean_json_response('  ["a"]  ') == '["a"]'

    def test_no_fence_returns_stripped(self):
        assert clean_json_response('  ["a"]  ') == '["a"]'

    def test_empty_string(self):
        assert clean_json_response("") == ""

    def test_only_fences(self):
        assert clean_json_response("``````") == ""


# ============================================================================
# parse_ai_posts
# ============================================================================

class TestParseAiPosts:
    def test_valid_json_5_posts(self):
        result = parse_ai_posts('["p1","p2","p3","p4","p5"]')
        assert len(result) == 5
        assert result == ["p1", "p2", "p3", "p4", "p5"]

    def test_valid_json_7_posts_truncated_to_5(self):
        result = parse_ai_posts('["p1","p2","p3","p4","p5","p6","p7"]')
        assert len(result) == 5

    def test_json_with_empty_strings_filtered(self):
        result = parse_ai_posts('["a","","b"]')
        assert result == ["a", "b"]

    def test_fenced_json_parsed(self):
        result = parse_ai_posts("```json\n[\"a\",\"b\"]\n```")
        assert result == ["a", "b"]

    def test_fallback_line_parsing_strips_post_prefix(self):
        result = parse_ai_posts("Post 1: Hello world\nPost 2: Another post")
        assert "Hello world" in result
        assert "Another post" in result

    def test_fallback_strips_numeric_prefix(self):
        result = parse_ai_posts("1. First post here\n2. Second post here")
        assert "First post here" in result
        assert "Second post here" in result

    def test_fallback_ignores_short_lines(self):
        # "hi" is < 10 chars, should be filtered out
        result = parse_ai_posts("hi\nPost 1: This is a long enough post")
        assert "This is a long enough post" in result
        assert "hi" not in result

    def test_empty_string_returns_empty_list(self):
        result = parse_ai_posts("")
        assert result == []

    def test_malformed_json_falls_back_to_lines(self):
        result = parse_ai_posts("not json\nPost 1: real content here")
        assert "real content here" in result

    def test_returns_max_5_from_fallback(self):
        result = parse_ai_posts(
            "Post 1: first post here\n"
            "Post 2: second post here\n"
            "Post 3: third post here\n"
            "Post 4: fourth post here\n"
            "Post 5: fifth post here\n"
            "Post 6: sixth post here\n"
            "Post 7: seventh post here"
        )
        assert len(result) == 5

    def test_whitespace_only_lines_filtered(self):
        result = parse_ai_posts(
            "Post 1: valid content here\n   \nPost 2: also valid content"
        )
        assert "valid content here" in result
        assert "also valid content" in result
        assert len(result) == 2

    def test_preserves_post_order(self):
        result = parse_ai_posts('["first","second","third","fourth","fifth"]')
        assert result[0] == "first"
        assert result[4] == "fifth"


# ============================================================================
# parse_ai_post_text
# ============================================================================

class TestParseAiPostText:
    def test_json_string_returned(self):
        result = parse_ai_post_text('"hello world"')
        assert result == "hello world"

    def test_fenced_json_string(self):
        result = parse_ai_post_text("```json\n\"hello\"\n```")
        assert result == "hello"

    def test_plain_text_returned(self):
        result = parse_ai_post_text("just text")
        assert result == "just text"

    def test_strips_surrounding_quotes(self):
        result = parse_ai_post_text('"quoted"')
        assert result == "quoted"

    def test_json_object_falls_back_to_text(self):
        # parse_ai_post_text only handles str, not dict
        result = parse_ai_post_text('{"a":1}')
        assert "a" in result

    def test_empty_string(self):
        result = parse_ai_post_text("")
        assert result == ""


# ============================================================================
# get_language_instruction
# ============================================================================

class TestGetLanguageInstruction:
    def test_arabic_returns_egyptian_instruction(self):
        result = get_language_instruction("ar")
        assert "Egyptian Arabic" in result

    def test_arabic_case_insensitive(self):
        result = get_language_instruction("Arabic")
        assert "Egyptian Arabic" in result

    def test_arabic_with_whitespace(self):
        result = get_language_instruction("  ar  ")
        assert "Egyptian Arabic" in result

    def test_english_returns_default_instruction(self):
        result = get_language_instruction("en")
        assert result == "the 'en' language"

    def test_french_returns_default_instruction(self):
        result = get_language_instruction("fr")
        assert result == "the 'fr' language"

    def test_none_returns_default_with_none(self):
        # Documents current behavior — None is passed through to f-string
        result = get_language_instruction(None)
        assert "None" in result

    def test_empty_string(self):
        result = get_language_instruction("")
        assert result == "the '' language"