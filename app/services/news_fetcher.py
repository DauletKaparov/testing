from datetime import datetime, timedelta
from typing import List

import feedparser

from ..models.article import ArticleCreate

# Free RSS feeds related to restaurants / business / QSR
FEED_CATEGORIES = {
    "fnb": [
        "https://news.google.com/rss/search?q=restaurant+OR+%22fast+food%22&hl=en-US&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=coffee+chain+OR+cafe&hl=en-US&gl=US&ceid=US:en",
    ],
    "tech": [
        "https://news.google.com/rss/search?q=technology+company+investment&hl=en-US&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=software+saas&hl=en-US&gl=US&ceid=US:en",
    ],
    "all": [
        "https://news.google.com/rss/search?q=business&hl=en-US&gl=US&ceid=US:en",
    ],
}

INDUSTRY_KEYWORDS = {
    "fnb": [
        "restaurant",
        "burger",
        "pizza",
        "coffee",
        "cafe",
        "chain",
        "dining",
        "menu",
    ],
    "tech": [
        "software",
        "ai",
        "cloud",
        "saas",
    ],
}


def _period_to_datetime(period: str) -> datetime:
    now = datetime.utcnow()
    if period == "day":
        return now - timedelta(days=1)
    if period == "week":
        return now - timedelta(days=7)
    if period == "month":
        return now - timedelta(days=30)
    raise ValueError("period must be one of day, week, month")


def fetch_recent_news(period: str, industry: str) -> List[ArticleCreate]:
    """Fetch basic news items from free RSS feeds within timeframe"""
    cutoff = _period_to_datetime(period)
    seen_urls = set()
    results: List[ArticleCreate] = []

    feeds = FEED_CATEGORIES.get(industry, FEED_CATEGORIES["all"])
    for feed_url in feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                published = datetime(*entry.updated_parsed[:6])

            if published and published < cutoff:
                continue  # outside time window

            url = entry.link
            if url in seen_urls:
                continue
            seen_urls.add(url)

            # keyword filter for additional relevance
            kw_list = INDUSTRY_KEYWORDS.get(industry, [])
            text_to_check = (entry.title + " " + getattr(entry, "summary", "")).lower()
            if kw_list and not any(k in text_to_check for k in kw_list):
                continue

            results.append(
                ArticleCreate(
                    title=entry.title,
                    content=getattr(entry, "summary", ""),
                    source=feed.feed.get("title", ""),
                    url=url,
                )
            )

            if len(results) >= 30:
                return results  # limit for MVP

    return results
