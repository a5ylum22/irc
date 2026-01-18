"""
State definition for the Investment Research LangGraph workflow.
This state flows through all agents in the graph.
"""

from typing import TypedDict, Optional, Dict, Any, List
from typing_extensions import Annotated
from operator import add


class InvestmentState(TypedDict):
    """
    State that flows through the agent graph.
    Each agent reads from and writes to this shared state.
    
    Flow:
    1. User provides ticker + query
    2. Coordinator plans the analysis
    3. Financial Agent + Sentiment Agent run in parallel
    4. Synthesizer combines results into final recommendation
    """
    
    # ===== INPUT =====
    ticker: str
    """Stock ticker symbol (e.g., 'NVDA', 'AAPL')"""
    
    user_query: str
    """User's question or investment query"""
    
    # ===== COORDINATOR OUTPUT =====
    analysis_plan: Optional[Dict[str, Any]]
    """Plan from coordinator about what analysis to perform"""
    
    # ===== AGENT OUTPUTS =====
    financial_analysis: Optional[Dict[str, Any]]
    """Output from Financial Agent (fundamentals + technical)"""
    
    sentiment_analysis: Optional[Dict[str, Any]]
    """Output from Sentiment Agent (news + market mood)"""
    
    # ===== SYNTHESIZER OUTPUT =====
    recommendation: Optional[Dict[str, Any]]
    """Final recommendation (BUY/HOLD/SELL)"""
    
    confidence: Optional[float]
    """Overall confidence score (0-1)"""
    
    reasoning: Optional[str]
    """Detailed reasoning for the recommendation"""
    
    # ===== METADATA =====
    messages: Annotated[List[Dict[str, str]], add]
    """List of messages for tracking agent execution (for debugging)"""
    
    errors: Annotated[List[str], add]
    """Any errors encountered during execution"""