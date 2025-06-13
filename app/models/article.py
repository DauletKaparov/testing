from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict

class Article(BaseModel):
    id: str
    title: str
    content: str
    source: str
    published_at: datetime
    url: str
    tickers: List[str] = []
    traffic_boosts: List[str] = []
    sentiment_score: Optional[float] = None
    impact_score: Optional[float] = None

class ArticleCreate(BaseModel):
    title: str
    content: str
    source: str
    url: str
    tickers: List[str] = []
    traffic_boosts: List[str] = []

# Response model for summarized news scan
class ArticleSummary(BaseModel):
    title: str
    brief: str
    why_matters: str
    tickers: List[str]
    prediction: Dict[str, str]
    score: float
    url: Optional[str]
