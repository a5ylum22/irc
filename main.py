"""
Main entry point for Investment Research Co-Pilot.
Run investment analysis on any stock ticker.
"""

import sys
from graph.workflow import create_workflow
from graph.state import InvestmentState
import json
from datetime import datetime


def run_analysis(ticker: str, user_query: str = None) -> dict:
    """
    Run complete investment analysis on a stock.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'NVDA', 'AAPL')
        user_query: Optional user question (default: "Should I invest in this stock?")
        
    Returns:
        Dict with complete analysis results
    """
    
    # Default query if none provided
    if not user_query:
        user_query = f"Should I invest in {ticker}?"
    
    print(f"\n{'='*60}")
    print(f"Investment Research Co-Pilot")
    print(f"{'='*60}")
    print(f"Ticker: {ticker.upper()}")
    print(f"Query: {user_query}")
    print(f"{'='*60}\n")
    
    # Create initial state
    initial_state = {
        "ticker": ticker.upper(),
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
    
    try:
        # Create and run workflow
        print("🔄 Creating workflow...")
        app = create_workflow()
        
        print("🚀 Running analysis...\n")
        
        # Execute the graph
        result = app.invoke(initial_state)
        
        # Print execution log
        print("\n📋 Execution Log:")
        for msg in result.get("messages", []):
            print(f"  [{msg['role']}] {msg['content']}")
        
        # Check for errors
        if result.get("errors"):
            print("\n⚠️  Errors encountered:")
            for error in result["errors"]:
                print(f"  - {error}")
        
        # Display results
        print("\n" + "="*60)
        print("ANALYSIS RESULTS")
        print("="*60)
        
        # Financial Analysis
        if result.get("financial_analysis"):
            print("\n📊 FINANCIAL ANALYSIS:")
            fin = result["financial_analysis"]
            print(f"  Assessment: {fin.get('assessment', 'N/A')}")
            print(f"  Valuation: {fin.get('valuation', 'N/A')}")
            print(f"  Trend: {fin.get('trend', 'N/A')}")
            
            if fin.get('strengths'):
                print("\n  Strengths:")
                for s in fin['strengths'][:3]:
                    print(f"    ✓ {s}")
            
            if fin.get('concerns'):
                print("\n  Concerns:")
                for c in fin['concerns'][:3]:
                    print(f"    ⚠ {c}")
        
        # Sentiment Analysis
        if result.get("sentiment_analysis"):
            print("\n📰 SENTIMENT ANALYSIS:")
            sent = result["sentiment_analysis"]
            print(f"  Overall Mood: {sent.get('overall_mood', 'N/A')}")
            print(f"  Sentiment Score: {sent.get('sentiment_score', 0):.2f}/1.0")
            print(f"  Articles Analyzed: {sent.get('article_count', 0)}")
            
            if sent.get('key_themes'):
                print("\n  Key Themes:")
                for theme in sent['key_themes'][:3]:
                    print(f"    • {theme}")
        
        # Final Recommendation
        if result.get("recommendation"):
            rec = result["recommendation"]
            action = rec.get("action", "UNKNOWN")
            confidence = result.get("confidence", 0)
            
            print("\n" + "="*60)
            print("🎯 FINAL RECOMMENDATION")
            print("="*60)
            print(f"\nAction: {action}")
            print(f"Confidence: {confidence:.1%}")
            print(f"Risk Level: {rec.get('risk_level', 'Unknown')}")
            print(f"Time Horizon: {rec.get('time_horizon', 'Unknown')}")
            print(f"\nReasoning:")
            print(f"{rec.get('reasoning', 'No reasoning provided')}")
            
            if rec.get('key_factors'):
                print(f"\nKey Factors:")
                for factor in rec['key_factors']:
                    print(f"  • {factor}")
            
            if rec.get('entry_strategy'):
                print(f"\nEntry Strategy:")
                print(f"  {rec['entry_strategy']}")
            
            if rec.get('watch_for'):
                print(f"\nRisks to Monitor:")
                for risk in rec['watch_for']:
                    print(f"  ⚠ {risk}")
        
        print("\n" + "="*60)
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error running analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


def save_result(result: dict, ticker: str):
    """
    Save analysis result to JSON file.
    
    Args:
        result: Analysis result dict
        ticker: Stock ticker
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analysis_{ticker}_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {filename}")


if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python main.py <TICKER> [QUERY]")
        print("\nExamples:")
        print("  python main.py NVDA")
        print("  python main.py AAPL 'Is this a good long-term investment?'")
        print("  python main.py TSLA 'Should I buy the dip?'")
        sys.exit(1)
    
    ticker = sys.argv[1]
    query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
    
    # Run analysis
    result = run_analysis(ticker, query)
    
    # Ask if user wants to save
    if result and not result.get("error"):
        save_choice = input("\nSave results to file? (y/n): ").strip().lower()
        if save_choice == 'y':
            save_result(result, ticker)