"""
URL Validator Utility
=====================
Validates and normalizes blog post URLs before processing.
"""

from urllib.parse import urlparse, urlunparse
import re


class URLValidator:
    """
    Validates and normalizes URLs for the content pipeline.

    Checks:
    - Valid URL format (scheme + netloc)
    - Supported schemes (http, https)
    - Not a blocked domain (social media, non-blog)
    - Reasonable URL length
    """

    # Domains that are NOT blog posts
    BLOCKED_DOMAINS = {
        "twitter.com", "x.com",
        "facebook.com", "fb.com",
        "instagram.com",
        "tiktok.com",
        "youtube.com", "youtu.be",
        "reddit.com",
        "linkedin.com",
        "pinterest.com",
        "snapchat.com",
    }

    MAX_URL_LENGTH = 2048

    @classmethod
    def validate(cls, url: str) -> tuple[bool, str]:
        """
        Validate a URL for blog scraping.

        Args:
            url: URL string to validate.

        Returns:
            Tuple of (is_valid, message).
        """
        if not url or not url.strip():
            return False, "URL cannot be empty"

        url = url.strip()

        if len(url) > cls.MAX_URL_LENGTH:
            return False, f"URL too long (max {cls.MAX_URL_LENGTH} characters)"

        # Parse URL
        parsed = urlparse(url)

        # Check scheme
        if parsed.scheme not in ("http", "https"):
            return False, "URL must start with http:// or https://"

        # Check netloc (domain)
        if not parsed.netloc:
            return False, "Invalid URL: missing domain"

        # Check blocked domains
        domain = parsed.netloc.lower().replace("www.", "")
        if domain in cls.BLOCKED_DOMAINS:
            return False, f"Social media URLs are not supported. Please paste a blog post URL."

        # Check for common file extensions that aren't articles
        path = parsed.path.lower()
        blocked_extensions = {".pdf", ".jpg", ".jpeg", ".png", ".gif", ".mp4", ".mp3", ".zip"}
        for ext in blocked_extensions:
            if path.endswith(ext):
                return False, f"File URLs ({ext}) are not supported. Please paste a blog post URL."

        return True, "Valid URL"

    @classmethod
    def normalize(cls, url: str) -> str:
        """
        Normalize a URL for consistent storage.

        - Strips whitespace
        - Removes trailing slashes
        - Removes tracking parameters (utm_*)
        - Lowercases scheme and domain
        """
        url = url.strip()
        parsed = urlparse(url)

        # Lowercase scheme and domain
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()

        # Remove tracking parameters
        query = parsed.query
        if query:
            params = query.split("&")
            filtered = [
                p for p in params
                if not p.startswith("utm_")
                and not p.startswith("ref=")
                and not p.startswith("source=")
            ]
            query = "&".join(filtered)

        # Remove trailing slash from path
        path = parsed.path.rstrip("/") if parsed.path != "/" else "/"

        return urlunparse((scheme, netloc, path, parsed.params, query, ""))
