"""
Tests for ContentScraper, SummarizerAI, and ContentPipeline.
Run with: pytest tests/ -v
"""

import pytest
from app.services.url_validator import URLValidator
from app.services.summarizer import MockSummarizer, SummarizerAI


# ===========================
# URL Validator Tests
# ===========================

class TestURLValidator:
    """Test URL validation and normalization."""

    def test_valid_blog_url(self):
        valid, msg = URLValidator.validate("https://overreacted.io/a-complete-guide-to-useeffect/")
        assert valid is True

    def test_valid_http_url(self):
        valid, msg = URLValidator.validate("http://blog.example.com/post")
        assert valid is True

    def test_empty_url(self):
        valid, msg = URLValidator.validate("")
        assert valid is False
        assert "empty" in msg.lower()

    def test_no_scheme(self):
        valid, msg = URLValidator.validate("blog.example.com/post")
        assert valid is False

    def test_blocked_twitter(self):
        valid, msg = URLValidator.validate("https://twitter.com/user/status/123")
        assert valid is False
        assert "social media" in msg.lower()

    def test_blocked_youtube(self):
        valid, msg = URLValidator.validate("https://youtube.com/watch?v=123")
        assert valid is False

    def test_blocked_file_extension(self):
        valid, msg = URLValidator.validate("https://example.com/file.pdf")
        assert valid is False
        assert ".pdf" in msg

    def test_url_too_long(self):
        long_url = "https://example.com/" + "a" * 3000
        valid, msg = URLValidator.validate(long_url)
        assert valid is False

    def test_normalize_removes_utm(self):
        url = "https://blog.example.com/post?utm_source=twitter&utm_medium=social&id=123"
        normalized = URLValidator.normalize(url)
        assert "utm_source" not in normalized
        assert "utm_medium" not in normalized
        assert "id=123" in normalized

    def test_normalize_removes_trailing_slash(self):
        url = "https://blog.example.com/post/"
        normalized = URLValidator.normalize(url)
        assert normalized == "https://blog.example.com/post"

    def test_normalize_lowercases_domain(self):
        url = "HTTPS://BLOG.EXAMPLE.COM/Post"
        normalized = URLValidator.normalize(url)
        assert normalized.startswith("https://blog.example.com")


# ===========================
# Mock Summarizer Tests
# ===========================

class TestMockSummarizer:
    """Test the mock summarizer for development."""

    @pytest.mark.asyncio
    async def test_mock_summarizer_returns_card(self):
        summarizer = MockSummarizer()
        card = await summarizer.summarize(
            "Some article text here...",
            {"title": "Test Post", "author": "Author", "url": "https://example.com"}
        )
        assert card.title == "Test Post"
        assert card.tl_dr is not None
        assert len(card.key_points) >= 3
        assert card.steal_insight is not None

    @pytest.mark.asyncio
    async def test_summarizer_ai_with_mock_strategy(self):
        """Test strategy pattern: inject mock into SummarizerAI."""
        ai = SummarizerAI(strategy=MockSummarizer())
        card = await ai.process(
            "Article content...",
            {"title": "Design Patterns", "author": "Gang of Four"}
        )
        assert card.title == "Design Patterns"
        assert card.author == "Gang of Four"

    @pytest.mark.asyncio
    async def test_strategy_swap_at_runtime(self):
        """Test that strategies can be swapped at runtime."""
        ai = SummarizerAI(strategy=MockSummarizer())

        # First call with mock
        card1 = await ai.process("text", {"title": "First"})
        assert card1.title == "First"

        # Swap strategy
        ai.set_strategy(MockSummarizer())

        # Second call still works
        card2 = await ai.process("text", {"title": "Second"})
        assert card2.title == "Second"
