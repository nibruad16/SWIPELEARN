"""
ContentScraper Service
======================
Component: ContentScraper
Pattern: Adapter Pattern (multiple scraping strategies)

Responsibility: Fetch and extract clean text content from any blog URL.
Input: URL string
Output: Clean text + metadata (title, author)
Dependencies: httpx, beautifulsoup4, readability-lxml
"""

import httpx
from bs4 import BeautifulSoup
from readability import Document
from urllib.parse import urlparse
from typing import Optional
import logging
import re

logger = logging.getLogger(__name__)


class ScrapedContent:
    """Data class for scraped content."""

    def __init__(
        self,
        title: str,
        author: Optional[str],
        text: str,
        url: str,
        domain: str,
    ):
        self.title = title
        self.author = author
        self.text = text
        self.url = url
        self.domain = domain

    def __repr__(self):
        return f"ScrapedContent(title='{self.title[:50]}...', author='{self.author}', text_length={len(self.text)})"


class ContentScraper:
    """
    Scrapes blog content from a URL and extracts clean text.

    Uses readability-lxml to extract main article content,
    then BeautifulSoup for fine-grained cleaning.
    """

    # Common user agents for scraping
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    # Maximum content length to process (characters)
    MAX_CONTENT_LENGTH = 50_000

    def __init__(self):
        self._client = httpx.AsyncClient(
            headers={"User-Agent": self.USER_AGENT},
            follow_redirects=True,
            timeout=30.0,
        )

    async def scrape(self, url: str) -> ScrapedContent:
        """
        Fetch and extract clean content from a blog URL.

        Args:
            url: The blog post URL to scrape.

        Returns:
            ScrapedContent with title, author, clean text, and metadata.

        Raises:
            ValueError: If URL is invalid or content cannot be extracted.
            httpx.HTTPError: If the HTTP request fails.
        """
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid URL: {url}")

        logger.info(f"Scraping URL: {url}")

        # Fetch HTML
        response = await self._client.get(url)
        response.raise_for_status()
        html = response.text

        # Extract main content using readability
        doc = Document(html)
        title = doc.title()
        content_html = doc.summary()

        # Clean HTML to text using BeautifulSoup
        soup = BeautifulSoup(content_html, "lxml")

        # Remove script and style elements
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()

        # Extract text
        text = soup.get_text(separator="\n", strip=True)

        # Clean up whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = text.strip()

        # Truncate if too long
        if len(text) > self.MAX_CONTENT_LENGTH:
            text = text[: self.MAX_CONTENT_LENGTH]
            logger.warning(f"Content truncated to {self.MAX_CONTENT_LENGTH} chars")

        # Extract author from meta tags
        author = self._extract_author(html)

        # Extract domain
        domain = parsed.netloc.replace("www.", "")

        if not text or len(text) < 100:
            raise ValueError("Could not extract meaningful content from URL")

        logger.info(
            f"Scraped: title='{title[:50]}', author='{author}', "
            f"text_length={len(text)}"
        )

        return ScrapedContent(
            title=title,
            author=author,
            text=text,
            url=url,
            domain=domain,
        )

    def _extract_author(self, html: str) -> Optional[str]:
        """Extract author name from HTML meta tags."""
        soup = BeautifulSoup(html, "lxml")

        # Try multiple meta tag patterns
        author_selectors = [
            {"name": "author"},
            {"property": "article:author"},
            {"name": "twitter:creator"},
            {"property": "og:author"},
        ]

        for selector in author_selectors:
            meta = soup.find("meta", attrs=selector)
            if meta and meta.get("content"):
                return meta["content"].strip()

        # Try common author element patterns
        author_elements = soup.select(
            '[class*="author"], [rel="author"], .byline, .post-author'
        )
        if author_elements:
            text = author_elements[0].get_text(strip=True)
            # Clean common prefixes
            text = re.sub(r"^(by|written by|author:?)\s*", "", text, flags=re.I)
            if text and len(text) < 100:
                return text

        return None

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
