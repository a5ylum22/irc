"""
Sentiment Agent - Analyzes news articles and market sentiment.
Uses NewsMCP to fetch news data and LLM to analyze sentiment.
"""

from graph.state import InvestmentState
from mcps.news import NewsMCP
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


def sentiment_agent(state: InvestmentState) -> InvestmentState:
    """
    Sentiment Agent - Analyzes news sentiment and market mood.
    
    Responsibilities:
    1. Fetch recent news articles about the stock
    2. Analyze sentiment of headlines and content
    3. Identify key themes and events
    4. Determine overall market mood (Bullish/Bearish/Neutral)
    
    Args:
        state: Current InvestmentState
        
    Returns:
        Updated state with sentiment_analysis
    """
    
    ticker = state.get("ticker")
    analysis_plan = state.get("analysis_plan", {})
    
    # Get company name from financial analysis if available
    company_name = None
    if state.get("financial_analysis"):
        raw_data = state["financial_analysis"].get("raw_data", {})
        company_info = raw_data.get("company_info", {})
        company_name = company_info.get("company_name")
    
    try:
        # Initialize News MCP
        news_mcp = NewsMCP()
        
        # Fetch news (last 30 days)
        news_data = news_mcp.fetch_data(ticker, company_name=company_name, days=30)
        
        if not news_data.get("success"):
            error_msg = f"Failed to fetch news: {news_data.get('error')}"
            state["errors"] = state.get("errors", []) + [error_msg]
            return state
        
        articles = news_data.get("articles", [])
        total_articles = len(articles)
        
        # If no articles found, return neutral sentiment
        if total_articles == 0:
            state["sentiment_analysis"] = {
                "sentiment_score": 0.5,
                "article_count": 0,
                "key_themes": [],
                "overall_mood": "Neutral",
                "concerns": ["No recent news coverage found"],
                "catalysts": [],
                "summary": "Insufficient news data to determine sentiment"
            }
            
            message = {
                "role": "sentiment_agent",
                "content": f"No news articles found for {ticker}"
            }
            state["messages"] = state.get("messages", []) + [message]
            return state
        
        # Build sentiment analysis prompt
        prompt = _build_sentiment_prompt(ticker, articles, analysis_plan)
        
        # Use LLM to analyze sentiment
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
            print(f"Warning: Failed to parse sentiment JSON: {e}")
            # If JSON parsing fails, create basic response
            analysis = {
                "sentiment_score": 0.5,
                "article_count": total_articles,
                "key_themes": [],
                "overall_mood": "Neutral",
                "concerns": [],
                "catalysts": [],
                "summary": response_text[:500]
            }
        
        # Ensure article_count is set
        analysis["article_count"] = total_articles
        
        # Add sample articles for reference
        analysis["sample_articles"] = articles[:5]  # Top 5 articles
        
        # Log message
        message = {
            "role": "sentiment_agent",
            "content": f"Analyzed {total_articles} articles for {ticker}. Mood: {analysis.get('overall_mood', 'Unknown')}"
        }
        
        return {"sentiment_analysis": analysis, "messages": [message]}
        
    except Exception as e:
        error_msg = f"Sentiment agent error: {str(e)}"
        return {"errors": state.get("errors", []) + [error_msg]}


def _build_sentiment_prompt(ticker: str, articles: list, plan: dict) -> str:
    """
    Build the prompt for LLM to analyze news sentiment.
    
    Args:
        ticker: Stock ticker
        articles: List of news articles
        plan: Analysis plan from coordinator
        
    Returns:
        Prompt string
    """
    
    # Take top 20 articles for analysis (to keep prompt manageable)
    top_articles = articles[:20]
    
    # Format articles for prompt
    articles_text = "\n\n".join([
        f"Article {i+1}:\n"
        f"Title: {article.get('title', 'No title')}\n"
        f"Source: {article.get('source', 'Unknown')}\n"
        f"Date: {article.get('published_at', 'Unknown')}\n"
        f"Description: {article.get('description', 'No description')}"
        for i, article in enumerate(top_articles)
    ])
    
    focus_areas = plan.get("focus_areas", ["comprehensive"])
    
    prompt = f"""You are a market sentiment analyst. Analyze the following news articles about {ticker}.

ARTICLES TO ANALYZE ({len(top_articles)} most recent):

{articles_text}

FOCUS AREAS: {', '.join(focus_areas)}

Based on these articles, provide sentiment analysis ONLY as a JSON object (no markdown, no code blocks):
{{
    "sentiment_score": 0.5,
    "overall_mood": "Bullish",
    "key_themes": ["theme 1", "theme 2", "theme 3"],
    "catalysts": ["positive factor 1", "positive factor 2"],
    "concerns": ["negative factor 1", "negative factor 2"],
    "summary": "2-3 sentence summary of overall sentiment and why"
}}

IMPORTANT: Return ONLY the JSON object. No explanations, no markdown code blocks, just the raw JSON.

Consider:
- Tone of headlines and content (positive vs negative)
- Recurring themes across articles
- Recent events or announcements
- Market reactions mentioned
- Analyst opinions cited

Be balanced and factual. Distinguish between hype and substance.
"""
    
    return prompt