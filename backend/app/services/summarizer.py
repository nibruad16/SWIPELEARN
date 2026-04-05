"""
SummarizerAI Service
====================
Component: SummarizerAI
Pattern: Strategy Pattern (swappable LLM providers)

Responsibility: Transform scraped blog content into structured Knowledge Cards.
Input: Clean text + metadata (title, author)
Output: KnowledgeCard JSON
Dependencies: OpenAI API (GPT-4o-mini)
"""

from abc import ABC, abstractmethod
from openai import AsyncOpenAI
from app.models.card import KnowledgeCardBase
from app.config import get_settings
import json
import logging

logger = logging.getLogger(__name__)


class SummarizerStrategy(ABC):
    """Abstract base class for summarization strategies."""

    @abstractmethod
    async def summarize(self, text: str, metadata: dict) -> KnowledgeCardBase:
        """
        Summarize text into a KnowledgeCard.

        Args:
            text: Clean article text.
            metadata: Dict with 'title', 'author', 'url' keys.

        Returns:
            KnowledgeCardBase with structured summary.
        """
        pass


class GPT4MiniSummarizer(SummarizerStrategy):
    """
    GPT-4o-mini based summarizer.
    Cost-efficient for high-volume summarization.
    """

    SYSTEM_PROMPT = """You are SwipeLearn AI — a knowledge extraction engine.
Your job is to transform blog posts into concise, high-value "Knowledge Cards"
that help busy learners absorb key ideas in seconds.

You MUST return valid JSON with this exact structure:
{
    "title": "The blog post title",
    "author": "Author name or null",
    "tl_dr": "One crisp sentence summarizing the entire article",
    "key_points": [
        "Key insight #1 — specific and actionable",
        "Key insight #2 — specific and actionable",
        "Key insight #3 — specific and actionable"
    ],
    "steal_insight": "One unique, actionable technique or idea the reader can immediately apply"
}

Rules:
- tl_dr: Maximum 1 sentence, under 30 words. Be punchy.
- key_points: 3-5 bullet points. Each should be a standalone insight.
- steal_insight: This is the "Steal Like an Artist" moment — the one thing
  worth remembering. Make it practical and specific.
- Use clear, simple language. No jargon unless the audience expects it.
- Preserve technical accuracy for engineering/design content.
"""

    def __init__(self, api_key: str | None = None):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=api_key or settings.openai_api_key)
        self.model = "gpt-4o-mini"

    async def summarize(self, text: str, metadata: dict) -> KnowledgeCardBase:
        """Summarize using GPT-4o-mini."""
        # Truncate text to fit context window (leaving room for prompt)
        max_chars = 12_000
        truncated_text = text[:max_chars]

        user_prompt = f"""Summarize this blog post into a Knowledge Card.

Title: {metadata.get('title', 'Unknown')}
Author: {metadata.get('author', 'Unknown')}
Source: {metadata.get('url', '')}

--- ARTICLE CONTENT ---
{truncated_text}
--- END CONTENT ---

Return the Knowledge Card as JSON."""

        logger.info(f"Sending to {self.model} for summarization...")

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=1000,
        )

        # Parse the response
        content = response.choices[0].message.content
        data = json.loads(content)

        logger.info(f"Summarization complete: {data.get('title', '')[:50]}")

        return KnowledgeCardBase(
            title=data.get("title", metadata.get("title", "Untitled")),
            author=data.get("author", metadata.get("author")),
            tl_dr=data["tl_dr"],
            key_points=data["key_points"],
            steal_insight=data["steal_insight"],
        )


class MockSummarizer(SummarizerStrategy):
    """
    Mock summarizer for testing without API calls.
    Returns deterministic test data.
    """

    async def summarize(self, text: str, metadata: dict) -> KnowledgeCardBase:
        return KnowledgeCardBase(
            title=metadata.get("title", "Test Article"),
            author=metadata.get("author", "Test Author"),
            tl_dr="This is a mock summary for testing purposes.",
            key_points=[
                "Key point 1: Testing is important",
                "Key point 2: Mock data helps development",
                "Key point 3: Strategy pattern enables swapping",
            ],
            steal_insight="Use the Strategy pattern to swap implementations without changing client code.",
        )


class SummarizerAI:
    """
    Main Summarizer service using Strategy Pattern.

    Allows swapping between different LLM providers
    (GPT-4o-mini, Claude, local models, mock) without
    changing the calling code.

    Usage:
        summarizer = SummarizerAI()  # defaults to GPT-4o-mini
        card = await summarizer.process(text, metadata)

        # Swap to mock for testing
        summarizer.set_strategy(MockSummarizer())
        card = await summarizer.process(text, metadata)
    """

    def __init__(self, strategy: SummarizerStrategy | None = None):
        self._strategy = strategy or GPT4MiniSummarizer()

    def set_strategy(self, strategy: SummarizerStrategy):
        """Swap the summarization strategy at runtime."""
        self._strategy = strategy

    async def process(self, text: str, metadata: dict) -> KnowledgeCardBase:
        """
        Process text through the active summarization strategy.

        Args:
            text: Clean article text.
            metadata: Dict with 'title', 'author', 'url' keys.

        Returns:
            KnowledgeCardBase with structured summary.
        """
        return await self._strategy.summarize(text, metadata)
