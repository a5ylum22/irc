"""
News MCP - Wrapper around NewsAPI for fetching stock-related news articles.
Provides recent news, headlines, and article metadata.
"""

from newsapi import NewsApiClient
from typing import Dict, Any, List
from datetime import datetime, timedelta
from .base import BaseMCP
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings


class NewsMCP(BaseMCP):
    """
    Provides news data including:
    - Recent news articles about a stock/company
    - Article metadata (title, source, publish date, URL)
    - Headline analysis
    """
    
    def __init__(self):
        """Initialize NewsMCP with NewsAPI client."""
        super().__init__()
        self.client = NewsApiClient(api_key=settings.NEWS_API_KEY)
        self.default_lookback_days = 30  # Default to last 30 days
    
    def fetch_data(self, ticker: str, company_name: str = None, days: int = None, **kwargs) -> Dict[str, Any]:
        """
        Fetch news articles for a given stock ticker.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'NVDA')
            company_name: Full company name for better search results (optional)
            days: Number of days to look back (default: 30)
            **kwargs: Additional parameters:
                - max_results: Maximum number of articles to return (default: 100)
                
        Returns:
            Dict containing:
                - success: bool
                - ticker: stock symbol
                - source: 'NewsAPI'
                - articles: list of article dicts
                - total_results: number of articles found
                - date_range: dict with from/to dates
        """
        try:
            days = days or self.default_lookback_days
            max_results = kwargs.get('max_results', 100)
            
            # Build search query
            query = self._build_query(ticker, company_name)
            
            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)
            
            # Fetch news from API
            response = self.client.get_everything(
                q=query,
                from_param=from_date.strftime('%Y-%m-%d'),
                to=to_date.strftime('%Y-%m-%d'),
                language='en',
                sort_by='relevancy',
                page_size=min(max_results, 100)  # API max is 100
            )
            
            articles = response.get('articles', [])
            
            # Process and structure articles
            processed_articles = self._process_articles(articles, ticker)
            
            return {
                "success": True,
                "ticker": ticker,
                "source": "NewsAPI",
                "articles": processed_articles,
                "total_results": len(processed_articles),
                "date_range": {
                    "from": from_date.isoformat(),
                    "to": to_date.isoformat(),
                    "days": days
                }
            }
            
        except Exception as e:
            return self.handle_error(e)
    
    def _build_query(self, ticker: str, company_name: str = None) -> str:
        """
        Build search query for NewsAPI.
        
        Combines ticker and company name for better results.
        
        Args:
            ticker: Stock ticker
            company_name: Full company name (optional)
            
        Returns:
            Query string for NewsAPI
        """
        if company_name:
            # Search for both ticker and company name
            # Use OR to cast a wider net
            return f'"{ticker}" OR "{company_name}"'
        else:
            # Just ticker
            return f'"{ticker}"'
    
    def _process_articles(self, articles: List[Dict], ticker: str) -> List[Dict[str, Any]]:
        """
        Process raw articles from API into structured format.
        
        Args:
            articles: Raw articles from NewsAPI
            ticker: Stock ticker (for filtering)
            
        Returns:
            List of processed article dicts
        """
        processed = []
        
        for article in articles:
            # Skip articles without essential fields
            if not article.get('title') or not article.get('publishedAt'):
                continue
            
            # Skip removed/deleted articles
            if article.get('title') == '[Removed]':
                continue
            
            processed_article = {
                "title": article.get('title'),
                "description": article.get('description', ''),
                "source": article.get('source', {}).get('name', 'Unknown'),
                "author": article.get('author'),
                "published_at": article.get('publishedAt'),
                "url": article.get('url'),
                "content_snippet": article.get('content', '')[:300] if article.get('content') else ''
            }
            
            processed.append(processed_article)
        
        # Sort by date (most recent first)
        processed.sort(key=lambda x: x['published_at'], reverse=True)
        
        return processed
    
    def get_top_headlines(self, ticker: str, company_name: str = None, max_results: int = 10) -> Dict[str, Any]:
        """
        Get just the top headlines (convenience method).
        
        Args:
            ticker: Stock ticker
            company_name: Full company name (optional)
            max_results: Number of top headlines to return (default: 10)
            
        Returns:
            Dict with top headlines
        """
        # Get last 7 days of news
        result = self.fetch_data(ticker, company_name, days=7)
        
        if result.get('success'):
            # Return only top N articles
            result['articles'] = result['articles'][:max_results]
            result['total_results'] = len(result['articles'])
        
        return result