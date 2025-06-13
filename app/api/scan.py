from fastapi import APIRouter, HTTPException, Query
from typing import List

from ..models.article import ArticleSummary
from ..services.summarizer import scan_period

router = APIRouter()

@router.get("/scan", response_model=List[ArticleSummary])
async def scan(period: str = Query("day", regex="^(day|week|month)$")):
    """Scan news within the given period (day|week|month) and return summaries"""
    try:
        return scan_period(period)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
