"""
FastAPI backend for Investment Research Co-Pilot.
Exposes the analysis workflow as a REST API for the frontend.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from graph.workflow import create_workflow
from graph.state import InvestmentState

app = FastAPI(
    title="Investment Research Co-Pilot API",
    description="Multi-agent AI system for stock analysis",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalysisRequest(BaseModel):
    """Request model for stock analysis."""
    ticker: str
    user_query: Optional[str] = None


class AnalysisResponse(BaseModel):
    """Response model for stock analysis."""
    ticker: str
    financial_analysis: Optional[dict] = None
    sentiment_analysis: Optional[dict] = None
    recommendation: Optional[dict] = None
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    messages: list = []
    errors: list = []


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Investment Research Co-Pilot API",
        "status": "running",
        "version": "1.0.0"
    }


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_stock(request: AnalysisRequest):
    """
    Analyze a stock and return investment recommendation.
    
    Args:
        request: Analysis request with ticker and optional query
        
    Returns:
        Complete analysis with recommendation
    """
    try:
        ticker = request.ticker.upper().strip()
        user_query = request.user_query or f"Should I invest in {ticker}?"
        
        # Validate ticker
        if not ticker or len(ticker) > 10:
            raise HTTPException(status_code=400, detail="Invalid ticker symbol")
        
        # Create initial state
        initial_state = {
            "ticker": ticker,
            "user_query": user_query,
            "analysis_plan": None,
            "financial_analysis": None,
            "sentiment_analysis": None,
            "recommendation": None,
            "confidence": None,
            "reasoning": None,
            "messages": [],
            "errors": []
        }
        
        # Create and run workflow
        workflow = create_workflow()
        result = workflow.invoke(initial_state)
        
        # Return results
        return AnalysisResponse(
            ticker=result.get("ticker"),
            financial_analysis=result.get("financial_analysis"),
            sentiment_analysis=result.get("sentiment_analysis"),
            recommendation=result.get("recommendation"),
            confidence=result.get("confidence"),
            reasoning=result.get("reasoning"),
            messages=result.get("messages", []),
            errors=result.get("errors", [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Investment Research Co-Pilot API...")
    print("📍 API will be available at: http://localhost:8000")
    print("📖 API docs available at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)