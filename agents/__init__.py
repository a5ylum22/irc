"""Agent implementations for Investment Research Co-Pilot."""

from .coordinator import coordinator_agent
from .financial_agent import financial_agent
from .sentiment_agent import sentiment_agent
from .synthesizer import synthesizer_agent

__all__ = [
    "coordinator_agent",
    "financial_agent",
    "sentiment_agent",
    "synthesizer_agent"
]