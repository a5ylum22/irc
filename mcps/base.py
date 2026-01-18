"""
Base class for MCP (Model Context Protocol) implementations.
Each MCP wraps a specific data source API.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseMCP(ABC):
    """
    Abstract base class for all MCP data source implementations.
    
    Each MCP is responsible for:
    1. Fetching data from a specific source (yfinance, NewsAPI, etc.)
    2. Handling errors gracefully
    3. Returning data in a consistent format
    """
    
    def __init__(self):
        """Initialize the MCP with its name."""
        self.name = self.__class__.__name__
        
    @abstractmethod
    def fetch_data(self, **kwargs) -> Dict[str, Any]:
        """
        Fetch data from the source.
        
        This method must be implemented by all subclasses.
        
        Args:
            **kwargs: Source-specific parameters (e.g., ticker, date range)
            
        Returns:
            Dict containing:
                - success: bool indicating if fetch succeeded
                - data: the fetched data
                - error: error message if success=False
                - source: name of the data source
        """
        pass
    
    def validate_params(self, **kwargs) -> bool:
        """
        Validate input parameters before fetching.
        
        Override in subclasses for specific validation logic.
        
        Args:
            **kwargs: Parameters to validate
            
        Returns:
            True if valid, raises ValueError if invalid
        """
        return True
    
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """
        Standardized error handling across all MCPs.
        
        Args:
            error: The exception that occurred
            
        Returns:
            Dict with error information
        """
        return {
            "success": False,
            "error": str(error),
            "error_type": type(error).__name__,
            "source": self.name
        }