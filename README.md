# NewsQuant MVP

A web-based platform for analyzing news articles and their potential market impact on cryptocurrencies/tickers.

## MVP Technical Roadmap

### Phase 1: Core Infrastructure (Week 1-2)
- [ ] Set up FastAPI backend with basic endpoints
- [ ] Implement basic news ingestion system (using RSS feeds)
- [ ] Set up Elasticsearch for storing news articles
- [ ] Create basic data models for articles and scores

### Phase 2: Basic Analysis (Week 3-4)
- [ ] Implement simple sentiment analysis using pre-trained model
- [ ] Create basic entity recognition for tickers
- [ ] Develop initial scoring system
- [ ] Add basic caching mechanism

### Phase 3: User Interface (Week 5-6)
- [ ] Create simple React frontend
- [ ] Implement article feed with basic filtering
- [ ] Add score visualization
- [ ] Add export functionality

### Phase 4: Testing & Optimization (Week 7)
- [ ] Set up unit tests
- [ ] Performance optimization
- [ ] Basic error handling
- [ ] Documentation

## Project Structure
```
newsquant/
├── app/
│   ├── api/          # FastAPI routes
│   ├── models/       # Data models
│   ├── services/     # Business logic
│   └── utils/        # Utility functions
├── frontend/         # React frontend
└── tests/           # Test files
```

## Technology Stack
- Backend: FastAPI, Python
- NLP: Transformers, PyTorch
- Database: Elasticsearch
- Frontend: React
- API: REST

## Getting Started

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
uvicorn app.main:app --reload
```

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.
