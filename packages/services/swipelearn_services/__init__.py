# SwipeLearn Services — Business logic components
"""
Service layer for the SwipeLearn platform.

Components:
- ContentScraper: Fetch & extract blog content (Adapter Pattern)
- SummarizerAI: AI-powered summarization (Strategy Pattern)
- TeacherTracker: Monitor blogs for new posts (Observer Pattern)
- FeedService: Feed generation & card management
- ContentPipeline: End-to-end URL → Knowledge Card pipeline
- URLValidator: URL validation and normalization

Install: pip install -e packages/services
"""

from swipelearn_services.scraper import ContentScraper, ScrapedContent
from swipelearn_services.summarizer import SummarizerAI, MockSummarizer
from swipelearn_services.feed_service import FeedService
from swipelearn_services.pipeline import ContentPipeline, PipelineResult
from swipelearn_services.teacher_tracker import TeacherTracker
from swipelearn_services.url_validator import URLValidator

__all__ = [
    "ContentScraper",
    "ScrapedContent",
    "SummarizerAI",
    "MockSummarizer",
    "FeedService",
    "ContentPipeline",
    "PipelineResult",
    "TeacherTracker",
    "URLValidator",
]
