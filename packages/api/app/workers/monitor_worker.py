"""
Teacher Monitor Worker
=======================
Background job that periodically checks teacher blogs for new posts.

Uses arq (async Redis queue) for job scheduling.
Runs on a cron schedule to check all teachers with RSS feeds.
"""

from arq import cron
from app.database import get_supabase_client
from swipelearn_services.teacher_tracker import TeacherTracker
from swipelearn_services.scraper import ContentScraper
from swipelearn_services.summarizer import SummarizerAI
from swipelearn_services.feed_service import FeedService
import logging

logger = logging.getLogger(__name__)


async def check_teacher_feeds(ctx: dict):
    """
    Check all teacher RSS feeds for new posts.
    
    For each teacher with an RSS feed:
    1. Fetch the RSS feed
    2. Find posts not yet in the database
    3. Scrape and summarize new posts
    4. Store as Knowledge Cards
    """
    logger.info("Starting teacher feed check...")
    
    db = get_supabase_client()
    tracker = TeacherTracker()
    scraper = ContentScraper()
    summarizer = SummarizerAI()
    feed_service = FeedService()

    try:
        # Get all teachers with RSS feeds
        result = db.table("teachers") \
            .select("*") \
            .not_.is_("blog_rss_url", "null") \
            .execute()

        teachers = result.data or []
        logger.info(f"Checking {len(teachers)} teachers with RSS feeds")

        total_new = 0

        for teacher in teachers:
            try:
                # Get known URLs for this teacher
                known_result = db.table("knowledge_cards") \
                    .select("source_url") \
                    .eq("teacher_id", teacher["id"]) \
                    .execute()
                known_urls = {r["source_url"] for r in (known_result.data or [])}

                # Fetch new posts
                new_posts = await tracker.fetch_new_posts(
                    teacher["blog_rss_url"],
                    known_urls=known_urls,
                    limit=5,
                )

                for post in new_posts:
                    try:
                        # Scrape the post
                        scraped = await scraper.scrape(post["url"])

                        # Summarize
                        metadata = {
                            "title": scraped.title or post["title"],
                            "author": teacher["name"],
                            "url": post["url"],
                        }
                        card_base = await summarizer.process(scraped.text, metadata)

                        # Store
                        card_data = {
                            "source_url": post["url"],
                            "title": card_base.title,
                            "author": card_base.author or teacher["name"],
                            "teacher_id": teacher["id"],
                            "tl_dr": card_base.tl_dr,
                            "key_points": card_base.key_points,
                            "steal_insight": card_base.steal_insight,
                            "raw_content": scraped.text[:5000],
                        }
                        await feed_service.store_card(card_data)
                        total_new += 1

                        logger.info(
                            f"New card from {teacher['name']}: {card_base.title[:50]}"
                        )

                    except Exception as e:
                        logger.error(
                            f"Error processing post {post['url']}: {e}"
                        )
                        continue

            except Exception as e:
                logger.error(
                    f"Error checking teacher {teacher['name']}: {e}"
                )
                continue

        logger.info(f"Feed check complete. {total_new} new cards created.")

    finally:
        await tracker.close()
        await scraper.close()


class WorkerSettings:
    """arq worker settings."""

    functions = [check_teacher_feeds]

    # Run every 6 hours
    cron_jobs = [
        cron(check_teacher_feeds, hour={0, 6, 12, 18}, minute=0),
    ]

    # Redis connection
    redis_settings = None  # Will be configured from env

    @classmethod
    def configure(cls, redis_url: str):
        """Configure Redis settings."""
        from arq.connections import RedisSettings
        from urllib.parse import urlparse

        parsed = urlparse(redis_url)
        cls.redis_settings = RedisSettings(
            host=parsed.hostname or "localhost",
            port=parsed.port or 6379,
            database=int(parsed.path.lstrip("/") or "0"),
        )
