"""
TeacherTracker Service
======================
Component: TeacherTracker
Pattern: Observer Pattern

Responsibility: Monitor teacher blogs for new posts via RSS.
Input: Teacher blog URL / RSS feed URL
Output: New post URLs to be scraped and summarized
Dependencies: feedparser, Supabase
"""

import feedparser
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TeacherTracker:
    """
    Monitors teacher blogs for new content.

    Discovers RSS feeds from blog URLs and checks for new posts
    that haven't been processed yet.
    """

    COMMON_RSS_PATHS = [
        "/feed",
        "/feed/",
        "/rss",
        "/rss/",
        "/atom.xml",
        "/feed.xml",
        "/rss.xml",
        "/index.xml",
        "/blog/feed",
        "/blog/rss",
    ]

    def __init__(self):
        self._client = httpx.AsyncClient(
            headers={
                "User-Agent": "SwipeLearn/1.0 (RSS Reader)"
            },
            follow_redirects=True,
            timeout=20.0,
        )

    async def discover_rss_feed(self, website_url: str) -> Optional[str]:
        """
        Discover RSS feed URL from a website.

        Tries:
        1. HTML <link> tags for RSS/Atom feeds
        2. Common RSS URL paths

        Args:
            website_url: The website URL to search for RSS.

        Returns:
            RSS feed URL if found, None otherwise.
        """
        logger.info(f"Discovering RSS feed for: {website_url}")

        try:
            # Step 1: Check HTML for feed links
            response = await self._client.get(website_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            feed_links = soup.find_all(
                "link",
                type=lambda t: t and ("rss" in t.lower() or "atom" in t.lower()),
            )

            if feed_links:
                href = feed_links[0].get("href")
                if href:
                    feed_url = urljoin(website_url, href)
                    logger.info(f"Found RSS feed via HTML: {feed_url}")
                    return feed_url

            # Step 2: Try common RSS paths
            parsed = urlparse(website_url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"

            for path in self.COMMON_RSS_PATHS:
                test_url = urljoin(base_url, path)
                try:
                    resp = await self._client.get(test_url)
                    if resp.status_code == 200 and (
                        "xml" in resp.headers.get("content-type", "")
                        or "rss" in resp.text[:500].lower()
                        or "atom" in resp.text[:500].lower()
                    ):
                        logger.info(f"Found RSS feed via path: {test_url}")
                        return test_url
                except httpx.HTTPError:
                    continue

        except httpx.HTTPError as e:
            logger.warning(f"Error discovering RSS for {website_url}: {e}")

        logger.info(f"No RSS feed found for: {website_url}")
        return None

    async def fetch_new_posts(
        self,
        rss_url: str,
        known_urls: set[str] | None = None,
        limit: int = 10,
    ) -> list[dict]:
        """
        Fetch new posts from an RSS feed.

        Args:
            rss_url: The RSS feed URL.
            known_urls: Set of already-processed URLs to skip.
            limit: Maximum number of new posts to return.

        Returns:
            List of dicts with 'title', 'url', 'published' keys.
        """
        known_urls = known_urls or set()

        logger.info(f"Fetching RSS: {rss_url}")

        try:
            response = await self._client.get(rss_url)
            response.raise_for_status()
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch RSS {rss_url}: {e}")
            return []

        feed = feedparser.parse(response.text)
        new_posts = []

        for entry in feed.entries[:limit * 2]:  # Check extra in case some are known
            url = entry.get("link", "")
            if not url or url in known_urls:
                continue

            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6])

            new_posts.append({
                "title": entry.get("title", "Untitled"),
                "url": url,
                "published": published,
                "author": entry.get("author", None),
            })

            if len(new_posts) >= limit:
                break

        logger.info(f"Found {len(new_posts)} new posts from {rss_url}")
        return new_posts

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
