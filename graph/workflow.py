"""
LangGraph workflow definition for Investment Research Co-Pilot.
Defines how agents are connected and execute.
"""

from langgraph.graph import StateGraph, END
from .state import InvestmentState
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_workflow():
    """
    Create and compile the LangGraph workflow.
    
    Workflow structure:
    
        User Input
            ↓
        Coordinator Agent (plans analysis)
            ↓
        ┌───────────────────────┐
        │                       │
    Financial Agent    Sentiment Agent
        │                       │
        └───────────┬───────────┘
                    ↓
            Synthesizer Agent
                    ↓
            Final Recommendation
    
    Returns:
        Compiled LangGraph workflow
    """
    
    # Import agents (we'll create these next)
    # For now, using placeholder functions
    from agents.coordinator import coordinator_agent
    from agents.financial_agent import financial_agent
    from agents.sentiment_agent import sentiment_agent
    from agents.synthesizer import synthesizer_agent
    
    # Create the graph
    workflow = StateGraph(InvestmentState)
    
    # Add nodes (agents)
    workflow.add_node("coordinator", coordinator_agent)
    workflow.add_node("financial_agent", financial_agent)
    workflow.add_node("sentiment_agent", sentiment_agent)
    workflow.add_node("synthesizer", synthesizer_agent)
    
    # Define the flow
    # Start with coordinator
    workflow.set_entry_point("coordinator")
    
    # Coordinator → both agents in parallel
    workflow.add_edge("coordinator", "financial_agent")
    workflow.add_edge("coordinator", "sentiment_agent")
    
    # Both agents → synthesizer
    workflow.add_edge("financial_agent", "synthesizer")
    workflow.add_edge("sentiment_agent", "synthesizer")
    
    # Synthesizer → end
    workflow.add_edge("synthesizer", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app


# For testing the graph structure
if __name__ == "__main__":
    print("Creating workflow...")
    app = create_workflow()
    print("✅ Workflow created successfully!")
    print("\nWorkflow structure:")
    print(app.get_graph().draw_ascii())