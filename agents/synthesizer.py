"""
Synthesizer Agent - Combines financial and sentiment analysis into final recommendation.
Last agent in the workflow.
"""

from graph.state import InvestmentState
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


def synthesizer_agent(state: InvestmentState) -> InvestmentState:
    """
    Synthesizer Agent - Generates final investment recommendation.
    
    Responsibilities:
    1. Combine financial analysis + sentiment analysis
    2. Weigh conflicting signals
    3. Generate BUY/HOLD/SELL recommendation
    4. Provide clear reasoning
    5. Assign confidence score
    
    Args:
        state: Current InvestmentState with financial_analysis and sentiment_analysis
        
    Returns:
        Updated state with recommendation, confidence, and reasoning
    """
    
    ticker = state.get("ticker")
    financial_analysis = state.get("financial_analysis", {})
    sentiment_analysis = state.get("sentiment_analysis", {})
    user_query = state.get("user_query", "")
    analysis_plan = state.get("analysis_plan", {})
    
    # Check if we have the required analyses
    if not financial_analysis or not sentiment_analysis:
        error_msg = "Missing required analysis data for synthesis"
        state["errors"] = state.get("errors", []) + [error_msg]
        return state
    
    try:
        # Build synthesis prompt
        prompt = _build_synthesis_prompt(
            ticker, 
            user_query,
            financial_analysis, 
            sentiment_analysis,
            analysis_plan
        )
        
        # Use LLM to synthesize
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
            recommendation = json.loads(cleaned_text)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Warning: Failed to parse recommendation JSON: {e}")
            # If JSON parsing fails, create basic recommendation
            recommendation = {
                "action": "HOLD",
                "confidence": 0.5,
                "reasoning": response_text[:1000],
                "risk_level": "Medium",
                "time_horizon": "Medium-term (3-12 months)",
                "key_factors": [],
                "entry_strategy": "Consult with a financial advisor",
                "watch_for": []
            }
        
        # Extract fields for state
        state["recommendation"] = recommendation
        state["confidence"] = recommendation.get("confidence", 0.5)
        state["reasoning"] = recommendation.get("reasoning", "")
        
        # Log message
        action = recommendation.get("action", "UNKNOWN")
        confidence = recommendation.get("confidence", 0)
        message = {
            "role": "synthesizer",
            "content": f"Final recommendation for {ticker}: {action} (confidence: {confidence:.2f})"
        }
        state["messages"] = state.get("messages", []) + [message]
        
    except Exception as e:
        error_msg = f"Synthesizer error: {str(e)}"
        state["errors"] = state.get("errors", []) + [error_msg]
    
    return state


def _build_synthesis_prompt(
    ticker: str,
    user_query: str,
    financial_analysis: dict,
    sentiment_analysis: dict,
    plan: dict
) -> str:
    """
    Build the prompt for LLM to synthesize final recommendation.
    
    Args:
        ticker: Stock ticker
        user_query: Original user question
        financial_analysis: Output from financial agent
        sentiment_analysis: Output from sentiment agent
        plan: Analysis plan
        
    Returns:
        Prompt string
    """
    
    # Extract key data
    fin_assessment = financial_analysis.get("assessment", "No assessment")
    fin_strengths = financial_analysis.get("strengths", [])
    fin_concerns = financial_analysis.get("concerns", [])
    fin_valuation = financial_analysis.get("valuation", "Unknown")
    fin_trend = financial_analysis.get("trend", "Unknown")
    
    sent_score = sentiment_analysis.get("sentiment_score", 0.5)
    sent_mood = sentiment_analysis.get("overall_mood", "Neutral")
    sent_themes = sentiment_analysis.get("key_themes", [])
    sent_catalysts = sentiment_analysis.get("catalysts", [])
    sent_concerns = sentiment_analysis.get("concerns", [])
    
    user_intent = plan.get("context", {}).get("user_intent", "research")
    
    prompt = f"""You are an investment advisor synthesizing analysis for {ticker}.

USER QUESTION: "{user_query}"
USER INTENT: {user_intent}

FINANCIAL ANALYSIS:
Assessment: {fin_assessment}
Valuation: {fin_valuation}
Price Trend: {fin_trend}

Strengths:
{chr(10).join(f"- {s}" for s in fin_strengths[:5])}

Concerns:
{chr(10).join(f"- {c}" for c in fin_concerns[:5])}

SENTIMENT ANALYSIS:
Overall Mood: {sent_mood}
Sentiment Score: {sent_score:.2f} (0=very negative, 1=very positive)

Key Themes:
{chr(10).join(f"- {t}" for t in sent_themes[:5])}

Positive Catalysts:
{chr(10).join(f"- {c}" for c in sent_catalysts[:3])}

Concerns from News:
{chr(10).join(f"- {c}" for c in sent_concerns[:3])}

Provide your final investment recommendation ONLY as a JSON object (no markdown, no code blocks):
{{
    "action": "BUY",
    "confidence": 0.75,
    "reasoning": "3-4 sentence explanation addressing both bull and bear cases",
    "risk_level": "Medium",
    "time_horizon": "Long-term (1+ years)",
    "key_factors": ["factor 1", "factor 2", "factor 3"],
    "entry_strategy": "Dollar-cost average over 3 months",
    "watch_for": ["risk 1 to monitor", "risk 2 to monitor"]
}}

IMPORTANT: Return ONLY the JSON object. No explanations, no markdown code blocks, just the raw JSON.

DECISION GUIDELINES:
- BUY: Strong fundamentals + positive sentiment, or significantly undervalued
- HOLD: Mixed signals, fairly valued, or insufficient conviction either way  
- SELL: Weak fundamentals + negative sentiment, or significantly overvalued

- Confidence >0.7: Strong conviction with aligned signals
- Confidence 0.5-0.7: Moderate conviction, some conflicting signals
- Confidence <0.5: Low conviction, highly conflicting signals

Be honest about uncertainty. If financial and sentiment signals conflict, explain the tradeoff clearly.
"""
    
    return prompt