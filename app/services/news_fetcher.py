from datetime import datetime, timedelta
from typing import List

import feedparser

from ..models.article import ArticleCreate

# Free RSS feeds related to restaurants / business / QSR
RSS_FEEDS = [
    "https://news.google.com/rss/search?q=restaurant+traffic+boost&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=fast+food+chain&hl=en-US&gl=US&ceid=US:en",
    "https://finance.yahoo.com/rss/topstories",
]


def _period_to_datetime(period: str) -> datetime:
    now = datetime.utcnow()
    if period == "day":
        return now - timedelta(days=1)
    if period == "week":
        return now - timedelta(days=7)
    if period == "month":
        return now - timedelta(days=30)
    raise ValueError("period must be one of day, week, month")


def fetch_recent_news(period: str) -> List[ArticleCreate]:
    """Fetch basic news items from free RSS feeds within timeframe"""
    cutoff = _period_to_datetime(period)
    seen_urls = set()
    results: List[ArticleCreate] = []

    for feed_url in RSS_FEEDS:
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
