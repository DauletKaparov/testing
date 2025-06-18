from typing import List, Dict
from transformers import pipeline, Pipeline
import re

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

# Summarizer will be loaded lazily to avoid long startup.
_summarizer: Pipeline | None = None


def _get_summarizer() -> Pipeline | None:
    global _summarizer
    if _summarizer is not None:
        return _summarizer

    try:
        # use much smaller t5-small model (~240MB)
        _summarizer = pipeline(
            "summarization",
            model="t5-small",
            tokenizer="t5-small",
            framework="pt",
            device=-1,
        )
    except Exception:
        _summarizer = None
    return _summarizer


def build_why_matters(categories: List[str]) -> str:
    if not categories:
        return "General sentiment news; no specific traffic-boost signal detected."
    return "; ".join(CATEGORY_EXPLANATIONS.get(cat, cat) for cat in categories)


# Neutral threshold to reduce noise
_NEUTRAL_THRESHOLD = 0.3

def predict_from_sentiment(sent: float) -> str | None:
    if sent > _NEUTRAL_THRESHOLD:
        return "Bullish"
    if sent < -_NEUTRAL_THRESHOLD:
        return "Bearish"
    return None


# Helpers
_TAG_RE = re.compile(r"<[^>]+>")
_URL_RE = re.compile(r"https?://\S+")


def _clean_text(raw: str) -> str:
    text = _TAG_RE.sub(" ", raw)
    text = _URL_RE.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


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

    cleaned_content = _clean_text(article.content)

    # Generate LLM-based brief summary (shock + impact)
    summarizer = _get_summarizer()
    if summarizer:
        try:
            llm_summary = summarizer(
                article.title + ". " + cleaned_content,
                max_length=40,
                min_length=15,
                do_sample=False,
            )[0]["summary_text"].strip()
        except Exception:
            llm_summary = cleaned_content[:200]
    else:
        llm_summary = cleaned_content[:200]

    prediction: Dict[str, str] = {
        t: pred for t in tickers if (pred := predict_from_sentiment(sent))
    } if tickers else {}

    if tickers and prediction:
        impact_part = "Potential impact: " + "; ".join(f"{t} {p}" for t, p in prediction.items())
    elif tickers:
        impact_part = "Potential impact: Equity relevance (sentiment unclear)"
    else:
        impact_part = "Potential impact: General industry sentiment"

    brief = f"{llm_summary} {impact_part}"
    why = build_why_matters(categories)

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
