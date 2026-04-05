"""
Content Pipeline Integration
=============================
End-to-end pipeline that connects ContentScraper → SummarizerAI → FeedService.
This is the core value chain of SwipeLearn.

Usage:
    pipeline = ContentPipeline()
    result = await pipeline.process_url("https://blog.example.com/article")
"""

from app.services.scraper import ContentScraper, ScrapedContent
from app.services.summarizer import SummarizerAI, MockSummarizer
from app.services.feed_service import FeedService
from app.models.card import KnowledgeCardBase
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PipelineResult:
    """Result of processing a URL through the content pipeline."""

    def __init__(
        self,
        scraped: ScrapedContent,
        card: KnowledgeCardBase,
        stored: Optional[dict] = None,
        teacher_linked: bool = False,
    ):
        self.scraped = scraped
        self.card = card
        self.stored = stored
        self.teacher_linked = teacher_linked

    @property
    def success(self) -> bool:
        return self.card is not None

    def to_dict(self) -> dict:
        return {
            "title": self.card.title,
            "author": self.card.author,
            "tl_dr": self.card.tl_dr,
            "key_points": self.card.key_points,
            "steal_insight": self.card.steal_insight,
            "source_url": self.scraped.url,
            "domain": self.scraped.domain,
        }


class ContentPipeline:
    """
    Orchestrates the full URL → Knowledge Card pipeline.

    Components:
    1. ContentScraper: Fetches and extracts clean text from URL
    2. SummarizerAI: Converts text into structured Knowledge Card
    3. FeedService: Stores the card in the database

    The pipeline is designed to be:
    - Fault-tolerant: Each step has independent error handling
    - Observable: Logging at each stage for debugging
    - Extensible: Components can be swapped via dependency injection
    """

    def __init__(
        self,
        scraper: Optional[ContentScraper] = None,
        summarizer: Optional[SummarizerAI] = None,
        feed_service: Optional[FeedService] = None,
    ):
        self.scraper = scraper or ContentScraper()
        self.summarizer = summarizer or SummarizerAI()
        self.feed_service = feed_service

    async def process_url(
        self,
        url: str,
        store: bool = True,
        teacher_id: Optional[str] = None,
    ) -> PipelineResult:
        """
        Process a URL through the full content pipeline.

        Args:
            url: Blog post URL to process.
            store: Whether to store the result in the database.
            teacher_id: Optional teacher ID to link the card to.

        Returns:
            PipelineResult with scraped content and knowledge card.

        Raises:
            ValueError: If URL is invalid or content cannot be extracted.
        """
        logger.info(f"Pipeline: Starting processing for {url}")

        # Stage 1: Scrape
        logger.info("Pipeline: Stage 1 — Scraping content")
        scraped = await self.scraper.scrape(url)
        logger.info(
            f"Pipeline: Scraped {len(scraped.text)} chars from {scraped.domain}"
        )

        # Stage 2: Summarize
        logger.info("Pipeline: Stage 2 — AI Summarization")
        metadata = {
            "title": scraped.title,
            "author": scraped.author,
            "url": url,
        }
        card = await self.summarizer.process(scraped.text, metadata)
        logger.info(f"Pipeline: Generated card: {card.title[:50]}")

        # Stage 3: Store (optional)
        stored = None
        if store and self.feed_service:
            logger.info("Pipeline: Stage 3 — Storing in database")
            card_data = {
                "source_url": url,
                "title": card.title,
                "author": card.author,
                "tl_dr": card.tl_dr,
                "key_points": card.key_points,
                "steal_insight": card.steal_insight,
                "raw_content": scraped.text[:5000],
            }
            if teacher_id:
                card_data["teacher_id"] = teacher_id

            try:
                stored = await self.feed_service.store_card(card_data)
                logger.info(f"Pipeline: Card stored with ID {stored.get('id')}")
            except Exception as e:
                logger.error(f"Pipeline: Storage failed: {e}")

        result = PipelineResult(
            scraped=scraped,
            card=card,
            stored=stored,
            teacher_linked=teacher_id is not None,
        )

        logger.info(f"Pipeline: Complete — success={result.success}")
        return result

    async def process_batch(
        self,
        urls: list[str],
        teacher_id: Optional[str] = None,
    ) -> list[PipelineResult]:
        """
        Process multiple URLs through the pipeline.
        Continues processing even if individual URLs fail.
        """
        results = []
        for url in urls:
            try:
                result = await self.process_url(
                    url, store=True, teacher_id=teacher_id
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Pipeline: Failed to process {url}: {e}")
                continue
        return results

    async def close(self):
        """Clean up resources."""
        await self.scraper.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
