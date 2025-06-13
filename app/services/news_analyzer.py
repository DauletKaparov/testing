from typing import List
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

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
        """Basic ticker extraction - this will be improved later"""
        # Simple pattern matching for now
        tickers = []
        words = text.split()
        for word in words:
            if word.isupper() and len(word) <= 5:
                tickers.append(word)
        return list(set(tickers))
    
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
