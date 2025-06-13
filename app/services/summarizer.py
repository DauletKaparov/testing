from typing import List, Dict

from .news_analyzer import NewsAnalyzer
from .news_fetcher import fetch_recent_news
from ..models.article import ArticleCreate, ArticleSummary

analyzer = NewsAnalyzer()

CATEGORY_EXPLANATIONS = {
    "management_change": "Leadership changes can shift company strategy and investor sentiment.",
    "store_remodelling": "Store remodels often drive higher foot traffic and sales uplift.",
    "tech_speed_accuracy": "Operational tech can improve service speed and order accuracy, boosting customer satisfaction.",
    "tech_digital_loyalty": "Digital investments and loyalty programs grow repeat visits and valuable first-party data.",
    "lto": "Limited-time menu items create urgency and can lead to traffic spikes.",
    "partnership": "Brand partnerships expand reach and create buzz, potentially attracting new customers.",
    "social_media_engagement": "Strong social buzz can translate into brand awareness and incremental visits.",
    "employee_engagement": "Happy employees generally deliver better service, supporting customer loyalty.",
}


def build_why_matters(categories: List[str]) -> str:
    if not categories:
        return "General sentiment news; no specific traffic-boost signal detected."
    return "; ".join(CATEGORY_EXPLANATIONS.get(cat, cat) for cat in categories)


def predict_from_sentiment(sent: float) -> str:
    return "Bullish" if sent > 0 else "Bearish"


def _score_article(sent: float, categories: List[str], tickers: List[str]) -> float:
    """Very simple heuristic 0-10 score"""
    score = 0.0
    score += len(categories) * 3  # importance of traffic boost signals
    score += 1.0 if tickers else 0.0  # equity relevance
    score += min(abs(sent) * 2, 2.0)  # sentiment magnitude up to 2 pts
    return min(score, 10.0)


def summarize_article(article: ArticleCreate) -> ArticleSummary:
    sent = analyzer.analyze_sentiment(article.content)
    tickers = analyzer.extract_tickers(article.content)
    categories = analyzer.detect_traffic_boosts(article.content)

    brief = (article.content[:200] + "…") if len(article.content) > 200 else article.content
    why = build_why_matters(categories)

    prediction = {t: predict_from_sentiment(sent) for t in tickers} if tickers else {}

    score = _score_article(sent, categories, tickers)

    return ArticleSummary(
        title=article.title,
        brief=brief,
        why_matters=why,
        tickers=tickers,
        prediction=prediction,
        url=article.url,
        score=score,
    )


def scan_period(period: str, industry: str) -> List[ArticleSummary]:
    raw_articles = fetch_recent_news(period, industry)
    summaries = [summarize_article(a) for a in raw_articles]
    return sorted(summaries, key=lambda s: s.score, reverse=True)
