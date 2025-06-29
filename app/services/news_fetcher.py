from datetime import datetime, timedelta
from typing import List

import feedparser

from ..models.article import ArticleCreate

# Free RSS feeds related to restaurants / business / QSR
FEED_CATEGORIES = {
    "fnb": [
        # General F&B news
        "https://news.google.com/rss/search?q=restaurant+OR+%22fast+food%22&hl=en-US&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=coffee+chain+OR+cafe&hl=en-US&gl=US&ceid=US:en",
        # Stock-specific queries for major publicly traded chains
        "https://news.google.com/rss/search?q=MCD+OR+SBUX+OR+CMG+OR+DPZ+OR+YUM+stock&hl=en-US&gl=US&ceid=US:en",
    ],
    "tech": [
        # General tech investing news
        "https://news.google.com/rss/search?q=technology+company+investment&hl=en-US&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=software+saas&hl=en-US&gl=US&ceid=US:en",
        # Stock-specific queries for big tech tickers
        "https://news.google.com/rss/search?q=TSLA+OR+AAPL+OR+MSFT+OR+AMZN+OR+GOOGL+OR+NVDA+stock&hl=en-US&gl=US&ceid=US:en",
    ],
    "all": [
        "https://news.google.com/rss/search?q=business&hl=en-US&gl=US&ceid=US:en",
    ],
}

INDUSTRY_KEYWORDS = {
    "fnb": [
        # Generic terms
        "restaurant",
        "burger",
        "pizza",
        "coffee",
        "cafe",
        "chain",
        "dining",
        "menu",
        # Major publicly-traded restaurant brands
        "mcdonald", "mcdonald's", "mcd", "burger king", "restaurant brands",
        "kfc", "taco bell", "yum brands", "chipotle", "cmg", "domino's", "dpz",
        "starbucks", "sbux", "wendy's", "wendys", "dnkn", "dunkin",
    ],
    "tech": [
        # Generic tech terms
        "software",
        "ai",
        "cloud",
        "saas",
        # Big tech company names / tickers
        "apple", "aapl", "tesla", "tsla", "microsoft", "msft", "amazon", "amzn",
        "google", "alphabet", "googl", "meta", "facebook", "meta platforms",
        "nvidia", "nvda", "netflix", "nflx", "intel", "intc",
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
