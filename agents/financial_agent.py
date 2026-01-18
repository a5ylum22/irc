"""
Financial Agent - Analyzes financial fundamentals and technical indicators.
Uses MarketDataMCP to fetch stock data.
"""

from graph.state import InvestmentState
from mcps.market_data import MarketDataMCP
from groq import Groq 
from config.settings import settings
import json
import re


def clean_json_response(response_text: str) -> str:
    """Clean LLM response to extract pure JSON."""
    response_text = response_text.strip()
    
    # Remove markdown code blocks
    if response_text.startswith("```"):
        lines = response_text.split('\n')
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        response_text = '\n'.join(lines).strip()
    
    # Extract JSON object
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if json_match:
        response_text = json_match.group(0)
    
    return response_text


def financial_agent(state: InvestmentState) -> InvestmentState:
    """
    Financial Agent - Performs fundamental and technical analysis.
    
    Responsibilities:
    1. Fetch stock data (fundamentals + price history)
    2. Analyze financial metrics (P/E, margins, growth, debt)
    3. Analyze technical indicators (moving averages, RSI, volatility)
    4. Generate assessment using LLM
    
    Args:
        state: Current InvestmentState
        
    Returns:
        Updated state with financial_analysis
    """
    
    ticker = state.get("ticker")
    analysis_plan = state.get("analysis_plan", {})
    
    try:
        # Initialize MCP
        market_data_mcp = MarketDataMCP()
        
        # Fetch all market data
        market_data = market_data_mcp.fetch_data(ticker, data_type="all", period="1y")
        
        if not market_data.get("success"):
            error_msg = f"Failed to fetch market data: {market_data.get('error')}"
            state["errors"] = state.get("errors", []) + [error_msg]
            return state
        
        # Extract data
        fundamentals = market_data.get("fundamentals", {})
        history = market_data.get("history", {})
        info = market_data.get("info", {})
        
        # Build analysis prompt
        prompt = _build_analysis_prompt(ticker, fundamentals, history, info, analysis_plan)
        
        # Use LLM to analyze
        client = Groq(api_key=settings.GROQ_API_KEY)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=settings.TEMPERATURE,
        )

        # Parse response (expecting JSON)
        response_text = response.choices[0].message.content
        
        try:
            cleaned_text = clean_json_response(response_text)
            analysis = json.loads(cleaned_text)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Warning: Failed to parse financial JSON: {e}")
            # If JSON parsing fails, create structured response
            analysis = {
                "fundamentals_summary": response_text[:500],
                "technical_summary": "See fundamentals summary",
                "assessment": response_text[:500],
                "strengths": [],
                "concerns": [],
                "valuation": "Unknown",
                "trend": "Unknown"
            }
        
        # Add raw data for reference
        analysis["raw_data"] = {
            "fundamentals": fundamentals,
            "technical": history,
            "company_info": info
        }
        
        # Log message
        message = {
            "role": "financial_agent",
            "content": f"Completed financial analysis for {ticker}"
        }
        
        return {"financial_analysis": analysis, "messages": [message]}
        
    except Exception as e:
        error_msg = f"Financial agent error: {str(e)}"
        return {"errors": state.get("errors", []) + [error_msg]}


def _build_analysis_prompt(ticker: str, fundamentals: dict, history: dict, info: dict, plan: dict) -> str:
    """
    Build the prompt for LLM to analyze financial data.
    
    Args:
        ticker: Stock ticker
        fundamentals: Financial metrics
        history: Price history with technical indicators
        info: Company info
        plan: Analysis plan from coordinator
        
    Returns:
        Prompt string
    """
    
    focus_areas = plan.get("focus_areas", ["comprehensive"])
    
    prompt = f"""You are a financial analyst. Analyze the following data for {ticker} ({info.get('company_name', 'Unknown')}).

COMPANY INFO:
- Sector: {info.get('sector', 'Unknown')}
- Industry: {info.get('industry', 'Unknown')}
- Market Cap: ${info.get('market_cap', 0):,.0f}

FUNDAMENTAL METRICS:
- P/E Ratio: {fundamentals.get('pe_ratio', 'N/A')}
- Forward P/E: {fundamentals.get('forward_pe', 'N/A')}
- Profit Margin: {fundamentals.get('profit_margin', 'N/A')}
- Revenue Growth: {fundamentals.get('revenue_growth', 'N/A')}
- Earnings Growth: {fundamentals.get('earnings_growth', 'N/A')}
- Debt-to-Equity: {fundamentals.get('debt_to_equity', 'N/A')}
- ROE: {fundamentals.get('roe', 'N/A')}
- Beta: {fundamentals.get('beta', 'N/A')}

TECHNICAL INDICATORS:
- Current Price: ${history.get('current_price', 'N/A')}
- 50-day MA: ${history.get('ma_50', 'N/A')}
- 200-day MA: ${history.get('ma_200', 'N/A')}
- RSI: {history.get('rsi', 'N/A')}
- 52-week High: ${history.get('52_week_high', 'N/A')}
- 52-week Low: ${history.get('52_week_low', 'N/A')}
- 1-month change: {history.get('price_change_1m', 'N/A')}%
- 3-month change: {history.get('price_change_3m', 'N/A')}%
- Volatility (annualized): {history.get('volatility', 'N/A')}%

FOCUS AREAS: {', '.join(focus_areas)}

Provide your analysis ONLY as a JSON object (no markdown, no code blocks):
{{
    "fundamentals_summary": "Brief summary of fundamental strength/weakness",
    "technical_summary": "Brief summary of technical indicators and price action",
    "assessment": "Overall financial assessment (2-3 sentences)",
    "strengths": ["strength 1", "strength 2", "strength 3"],
    "concerns": ["concern 1", "concern 2", "concern 3"],
    "valuation": "Overvalued/Fairly Valued/Undervalued",
    "trend": "Upward/Downward/Sideways"
}}

IMPORTANT: Return ONLY the JSON object. No explanations, no markdown code blocks, just the raw JSON.

Be concise, factual, and balanced. Consider both bull and bear cases.
"""
    
    return prompt