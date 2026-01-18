"""
Pydantic models for type safety and data validation.
These schemas define the structure of data flowing through the system.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class FinancialMetrics(BaseModel):
    """Financial metrics from fundamental analysis."""
    pe_ratio: Optional[float] = Field(None, description="Price-to-Earnings ratio")
    industry_avg_pe: Optional[float] = Field(None, description="Industry average P/E ratio")
    revenue_growth: Optional[str] = Field(None, description="Year-over-year revenue growth")
    profit_margin: Optional[float] = Field(None, description="Net profit margin percentage")
    debt_to_equity: Optional[float] = Field(None, description="Debt-to-equity ratio")
    current_price: Optional[float] = Field(None, description="Current stock price")


class TechnicalIndicators(BaseModel):
    """Technical analysis indicators."""
    trend: str = Field(..., description="Overall price trend (Upward/Downward/Sideways)")
    ma_50: Optional[float] = Field(None, description="50-day moving average")
    ma_200: Optional[float] = Field(None, description="200-day moving average")
    rsi: Optional[float] = Field(None, description="Relative Strength Index (0-100)")
    signal: str = Field(..., description="Technical analysis signal")
    support_level: Optional[float] = Field(None, description="Support price level")
    resistance_level: Optional[float] = Field(None, description="Resistance price level")


class FinancialAnalysis(BaseModel):
    """Complete financial analysis output from Financial Agent."""
    fundamentals: FinancialMetrics
    technical: TechnicalIndicators
    assessment: str = Field(..., description="Overall financial assessment")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")


class SentimentAnalysis(BaseModel):
    """Sentiment analysis output from Sentiment Agent."""
    sentiment_score: float = Field(..., ge=0.0, le=1.0, description="Overall sentiment (0=very negative, 1=very positive)")
    article_count: int = Field(..., description="Number of articles analyzed")
    key_themes: List[str] = Field(default_factory=list, description="Main themes from news")
    overall_mood: str = Field(..., description="Overall market mood (Bullish/Bearish/Neutral)")
    concerns: List[str] = Field(default_factory=list, description="Identified concerns or risks")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")


class Recommendation(BaseModel):
    """Final investment recommendation."""
    action: str = Field(..., description="Recommended action (BUY/SELL/HOLD)")
    reasoning: str = Field(..., description="Detailed reasoning for recommendation")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence (0-1)")
    risk_level: str = Field(..., description="Risk level (Low/Medium/High)")
    time_horizon: str = Field(..., description="Recommended investment time horizon")
    key_factors: List[str] = Field(default_factory=list, description="Key decision factors")
    sources: List[str] = Field(default_factory=list, description="Data sources used")


class InvestmentState(BaseModel):
    """
    State object that flows through the LangGraph workflow.
    Each agent reads from and writes to this state.
    """
    # Input
    ticker: str = Field(..., description="Stock ticker symbol")
    user_query: str = Field(default="Should I invest in this stock?", description="User's question")
    
    # Coordinator output
    analysis_plan: Optional[Dict[str, Any]] = Field(None, description="Analysis plan from coordinator")
    
    # Agent outputs
    financial_analysis: Optional[FinancialAnalysis] = Field(None, description="Financial agent output")
    sentiment_analysis: Optional[SentimentAnalysis] = Field(None, description="Sentiment agent output")
    
    # Final output
    recommendation: Optional[Recommendation] = Field(None, description="Final recommendation")
    
    # Metadata
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")
    
    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True


class StockInfo(BaseModel):
    """Basic stock information from market data."""
    ticker: str
    company_name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    description: Optional[str] = None


class NewsArticle(BaseModel):
    """Individual news article."""
    title: str
    description: Optional[str] = None
    url: str
    published_at: str
    source: str
    sentiment: Optional[float] = Field(None, ge=-1.0, le=1.0, description="Article sentiment (-1 to 1)")