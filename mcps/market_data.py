"""
Market Data MCP - Wrapper around yfinance for stock market data.
Provides stock prices, fundamentals, and technical indicators.
"""

import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional
from .base import BaseMCP


class MarketDataMCP(BaseMCP):
    """
    Provides stock market data including:
    - Current price and basic company info
    - Financial fundamentals (P/E ratio, margins, revenue growth, etc.)
    - Historical price data for technical analysis
    - Technical indicators (moving averages, RSI, volatility)
    """
    
    def fetch_data(self, ticker: str, data_type: str = "all", **kwargs) -> Dict[str, Any]:
        """
        Fetch market data for a given ticker symbol.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'NVDA', 'TSLA')
            data_type: Type of data to fetch:
                - 'info': Basic stock info
                - 'history': Historical price data
                - 'fundamentals': Financial metrics
                - 'all': Everything (default)
            **kwargs: Additional parameters:
                - period: Time period for history (e.g., '1y', '6mo', '1mo')
                
        Returns:
            Dict containing:
                - success: bool
                - ticker: stock symbol
                - source: 'yfinance'
                - info: basic stock info (if requested)
                - history: price history with technical indicators (if requested)
                - fundamentals: financial metrics (if requested)
        """
        try:
            # Validate ticker
            if not ticker or not isinstance(ticker, str):
                raise ValueError("Ticker must be a non-empty string")
            
            ticker = ticker.upper()
            stock = yf.Ticker(ticker)
            
            result = {
                "success": True,
                "ticker": ticker,
                "source": "yfinance"
            }
            
            # Fetch requested data types
            if data_type in ["info", "all"]:
                result["info"] = self._get_stock_info(stock)
            
            if data_type in ["history", "all"]:
                period = kwargs.get("period", "1y")
                result["history"] = self._get_price_history(stock, period)
            
            if data_type in ["fundamentals", "all"]:
                result["fundamentals"] = self._get_fundamentals(stock)
                
            return result
            
        except Exception as e:
            return self.handle_error(e)
    
    def _get_stock_info(self, stock: yf.Ticker) -> Dict[str, Any]:
        """
        Get basic stock information.
        
        Args:
            stock: yfinance Ticker object
            
        Returns:
            Dict with company name, sector, industry, market cap, etc.
        """
        info = stock.info
        return {
            "company_name": info.get("longName", info.get("shortName", "Unknown")),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "market_cap": info.get("marketCap"),
            "current_price": info.get("currentPrice", info.get("regularMarketPrice")),
            "currency": info.get("currency", "USD"),
            "exchange": info.get("exchange"),
            "description": info.get("longBusinessSummary", "")[:500]  # First 500 chars
        }
    
    def _get_price_history(self, stock: yf.Ticker, period: str) -> Dict[str, Any]:
        """
        Get historical price data with technical indicators.
        
        Args:
            stock: yfinance Ticker object
            period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max')
            
        Returns:
            Dict with current price, moving averages, RSI, volatility, etc.
        """
        hist = stock.history(period=period)
        
        if hist.empty:
            return {"error": "No historical data available"}
        
        # Calculate technical indicators
        hist['MA_50'] = hist['Close'].rolling(window=50).mean()
        hist['MA_200'] = hist['Close'].rolling(window=200).mean()
        
        current_price = hist['Close'].iloc[-1]
        ma_50 = hist['MA_50'].iloc[-1]
        ma_200 = hist['MA_200'].iloc[-1]
        
        # Calculate RSI (Relative Strength Index)
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Calculate volatility (annualized standard deviation)
        daily_returns = hist['Close'].pct_change()
        volatility = daily_returns.std() * (252 ** 0.5) * 100  # 252 trading days/year
        
        # Price changes
        price_1m_ago = hist['Close'].iloc[-21] if len(hist) >= 21 else hist['Close'].iloc[0]
        price_3m_ago = hist['Close'].iloc[-63] if len(hist) >= 63 else hist['Close'].iloc[0]
        
        return {
            "current_price": float(current_price),
            "ma_50": float(ma_50) if not pd.isna(ma_50) else None,
            "ma_200": float(ma_200) if not pd.isna(ma_200) else None,
            "rsi": float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None,
            "52_week_high": float(hist['High'].max()),
            "52_week_low": float(hist['Low'].min()),
            "price_change_1m": float((current_price - price_1m_ago) / price_1m_ago * 100),
            "price_change_3m": float((current_price - price_3m_ago) / price_3m_ago * 100),
            "volatility": float(volatility),
            "volume_avg": float(hist['Volume'].mean())
        }
    
    def _get_fundamentals(self, stock: yf.Ticker) -> Dict[str, Any]:
        """
        Get fundamental financial metrics.
        
        Args:
            stock: yfinance Ticker object
            
        Returns:
            Dict with P/E ratio, profit margins, growth rates, debt ratios, etc.
        """
        info = stock.info
        
        return {
            # Valuation metrics
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "peg_ratio": info.get("pegRatio"),
            "price_to_book": info.get("priceToBook"),
            "price_to_sales": info.get("priceToSalesTrailing12Months"),
            
            # Profitability metrics
            "profit_margin": info.get("profitMargins"),
            "operating_margin": info.get("operatingMargins"),
            "gross_margin": info.get("grossMargins"),
            "roe": info.get("returnOnEquity"),
            "roa": info.get("returnOnAssets"),
            
            # Growth metrics
            "revenue_growth": info.get("revenueGrowth"),
            "earnings_growth": info.get("earningsGrowth"),
            "earnings_quarterly_growth": info.get("earningsQuarterlyGrowth"),
            
            # Financial health
            "debt_to_equity": info.get("debtToEquity"),
            "current_ratio": info.get("currentRatio"),
            "quick_ratio": info.get("quickRatio"),
            
            # Risk metrics
            "beta": info.get("beta"),
            
            # Dividend info
            "dividend_yield": info.get("dividendYield"),
            "payout_ratio": info.get("payoutRatio"),
            
            # Analyst opinions
            "analyst_recommendation": info.get("recommendationKey"),
            "target_mean_price": info.get("targetMeanPrice"),
            "number_of_analyst_opinions": info.get("numberOfAnalystOpinions")
        }