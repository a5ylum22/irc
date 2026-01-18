"""
Coordinator Agent - Plans and orchestrates the investment analysis.
First agent in the workflow.
"""

from graph.state import InvestmentState
from typing import Dict, Any


def coordinator_agent(state: InvestmentState) -> InvestmentState:
    """
    Coordinator Agent - Plans the analysis strategy.
    
    Responsibilities:
    1. Validate input (ticker, query)
    2. Determine analysis focus based on user query
    3. Set context for downstream agents
    
    Args:
        state: Current InvestmentState
        
    Returns:
        Updated state with analysis_plan
    """
    
    ticker = state.get("ticker", "").upper().strip()
    user_query = state.get("user_query", "Should I invest in this stock?")
    
    # Validate ticker
    if not ticker:
        state["errors"] = state.get("errors", []) + ["No ticker provided"]
        return state
    
    # Create analysis plan
    # For MVP, we always do both financial and sentiment analysis
    # In future, could be smarter based on query
    analysis_plan = {
        "ticker": ticker,
        "perform_financial_analysis": True,
        "perform_sentiment_analysis": True,
        "focus_areas": _determine_focus_areas(user_query),
        "context": {
            "user_intent": _classify_user_intent(user_query),
            "time_sensitivity": _assess_time_sensitivity(user_query)
        }
    }
    
    # Log message
    message = {
        "role": "coordinator",
        "content": f"Planning analysis for {ticker}. Focus: {', '.join(analysis_plan['focus_areas'])}"
    }
    
    # Update state
    state["analysis_plan"] = analysis_plan
    state["messages"] = state.get("messages", []) + [message]
    
    return {"analysis_plan": analysis_plan, "messages": [message]}


def _determine_focus_areas(user_query: str) -> list:
    """
    Determine what aspects to focus on based on user query.
    
    Keywords analysis:
    - "risk", "risky", "safe" → focus on risk metrics
    - "value", "fundamental", "earnings" → focus on fundamentals
    - "price", "trend", "momentum" → focus on technical analysis
    - "news", "sentiment" → focus on news/sentiment
    
    Args:
        user_query: User's question
        
    Returns:
        List of focus areas
    """
    query_lower = user_query.lower()
    focus_areas = []
    
    # Risk-related
    if any(word in query_lower for word in ["risk", "risky", "safe", "volatile", "volatility"]):
        focus_areas.append("risk_assessment")
    
    # Fundamentals
    if any(word in query_lower for word in ["value", "fundamental", "earnings", "revenue", "profit"]):
        focus_areas.append("fundamentals")
    
    # Technical analysis
    if any(word in query_lower for word in ["price", "trend", "momentum", "technical", "chart"]):
        focus_areas.append("technical")
    
    # News/sentiment
    if any(word in query_lower for word in ["news", "sentiment", "recent", "latest", "happening"]):
        focus_areas.append("news_sentiment")
    
    # Default: comprehensive analysis
    if not focus_areas:
        focus_areas = ["comprehensive"]
    
    return focus_areas


def _classify_user_intent(user_query: str) -> str:
    """
    Classify what the user is trying to do.
    
    Args:
        user_query: User's question
        
    Returns:
        One of: "buy_decision", "sell_decision", "hold_decision", "research"
    """
    query_lower = user_query.lower()
    
    if any(word in query_lower for word in ["buy", "invest", "purchase", "should i get"]):
        return "buy_decision"
    elif any(word in query_lower for word in ["sell", "exit", "dump", "get out"]):
        return "sell_decision"
    elif any(word in query_lower for word in ["hold", "keep", "maintain", "stay in"]):
        return "hold_decision"
    else:
        return "research"


def _assess_time_sensitivity(user_query: str) -> str:
    """
    Assess if user needs urgent/time-sensitive information.
    
    Args:
        user_query: User's question
        
    Returns:
        "urgent" or "normal"
    """
    query_lower = user_query.lower()
    
    urgent_keywords = ["today", "now", "urgent", "immediate", "asap", "quick", "right now"]
    
    if any(word in query_lower for word in urgent_keywords):
        return "urgent"
    
    return "normal"