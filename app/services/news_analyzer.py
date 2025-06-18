from typing import List
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re

# Keywords for identifying traffic boost categories
TRAFFIC_BOOST_KEYWORDS = {
    "management_change": [
        "new ceo", "new cfo", "new coo", "new cmo", "new cto", "steps down as ceo", "resigns as ceo", "appointed ceo", "leadership change", "executive shakeup"
    ],
    "store_remodelling": [
        "store remodel", "store remodelling", "reimage program", "revamp stores", "store renovation", "store facelift"
    ],
    "tech_speed_accuracy": [
        "kitchen display system", "kds", "ai algorithm", "order accuracy", "speed of service", "drive thru tech", "robotic", "automation", "self checkout", "self-order kiosk"
    ],
    "tech_digital_loyalty": [
        "mobile app", "loyalty program", "reward members", "digital sales", "online order", "delivery app", "first-party data", "guest data", "crm"
    ],
    "lto": [
        "limited time offer", "lto", "seasonal menu", "special menu", "limited edition", "promo for a limited time", "returns for a limited time"
    ],
    "partnership": [
        "partners with", "collaboration with", "teams up with", "partnership", "joint venture"
    ],
    "social_media_engagement": [
        "tiktok challenge", "viral on tiktok", "trending on twitter", "instagram campaign", "social media buzz", "meme" 
    ],
    "employee_engagement": [
        "best place to work", "employee satisfaction", "glassdoor rating", "wage increase", "tuition assistance", "staff happiness", "employee wellness", "retention"
    ]
}

class NewsAnalyzer:
    def __init__(self):
        self._senti = SentimentIntensityAnalyzer()
        
    def analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of the text and return a score between -1 and 1"""
        return self._senti.polarity_scores(text)["compound"]
    
    def extract_tickers(self, text: str) -> List[str]:
        """
        Extract potential stock tickers from the given text.

        Heuristics:
        1. Detect typical market notations like $TSLA, (TSLA), NASDAQ:TSLA, NYSE:TSLA.
        2. Capture standalone upper-case tokens 2-5 characters long.
        3. Filter out common English stop-words to minimise false positives.
        """
        # Strict patterns to avoid false positives: require a financial marker
        pattern = re.compile(r"(?:\$|\bNASDAQ:|\bNYSE:)(?P<tkr>[A-Z]{2,5})\b")
        candidates = {m.group("tkr") for m in pattern.finditer(text)}

        # Remove obvious stop words / non-ticker tokens.
        stopwords = {
            "THE",
            "AND",
            "FOR",
            "WITH",
            "THIS",
            "THAT",
            "FROM",
            "WILL",
            "WHAT",
            "WHEN",
            "WHERE",
            "WHICH",
            "MORE",
            "NEWS",
        }
        tickers = {tkr for tkr in candidates if tkr not in stopwords}

        # 2) Company‐name lookup fallback
        company_map = {
            # expand as needed – avoid overly generic terms like "google"
            "tesla": "TSLA",
            "microsoft": "MSFT",
            "apple": "AAPL",
            "amazon": "AMZN",
            "alphabet": "GOOGL",
            "meta": "META",
            "facebook": "META",
            "nvidia": "NVDA",
            "netflix": "NFLX",
        }

        # Strip URLs to avoid picking up company names inside link domains (e.g. news.google.com)
        url_stripped = re.sub(r"https?://\S+", " ", text, flags=re.IGNORECASE).lower()

        for name, tkr in company_map.items():
            if re.search(rf"\b{re.escape(name)}\b", url_stripped):
                tickers.add(tkr)

        return sorted(tickers)
    
    def calculate_impact_score(self, sentiment_score: float, tickers: List[str]) -> float:
        """Calculate basic impact score"""
        # For MVP, just use sentiment score as impact score
        # Will be improved with more features later
        return abs(sentiment_score)

    def detect_traffic_boosts(self, text: str) -> List[str]:
        """Detect traffic‐boost related categories mentioned in the text"""
        lower_text = text.lower()
        found: List[str] = []
        for category, keywords in TRAFFIC_BOOST_KEYWORDS.items():
            for kw in keywords:
                if kw in lower_text:
                    found.append(category)
                    break  # only need one keyword to match
        return found
