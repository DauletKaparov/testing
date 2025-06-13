from fastapi import APIRouter, HTTPException
from ..models.article import Article, ArticleCreate
from ..services.news_analyzer import NewsAnalyzer
from datetime import datetime
import uuid

router = APIRouter()
analyzer = NewsAnalyzer()

@router.post("/analyze", response_model=Article)
async def analyze_article(article: ArticleCreate):
    """Analyze a news article and return scores"""
    try:
        # Generate unique ID
        article_id = str(uuid.uuid4())
        
        # Analyze sentiment
        sentiment_score = analyzer.analyze_sentiment(article.content)
        
        # Extract tickers
        tickers = analyzer.extract_tickers(article.content)
        
        # Detect traffic boost categories
        traffic_boosts = analyzer.detect_traffic_boosts(article.content)
        
        # Calculate impact score
        impact_score = analyzer.calculate_impact_score(sentiment_score, tickers)
        
        return Article(
            id=article_id,
            title=article.title,
            content=article.content,
            source=article.source,
            url=article.url,
            published_at=datetime.now(),
            tickers=tickers,
            traffic_boosts=traffic_boosts,
            sentiment_score=sentiment_score,
            impact_score=impact_score
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
