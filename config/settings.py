"""
Configuration settings for the Investment Research Co-Pilot.
Loads environment variables and provides app-wide configuration.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Model Configuration
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gemini-pro")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE: int = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "60"))
    
    # Data Source Configuration
    NEWS_LOOKBACK_DAYS: int = 30  # How many days of news to fetch
    STOCK_HISTORY_PERIOD: str = "1y"  # Stock price history period
    
    # Agent Configuration
    MAX_AGENT_RETRIES: int = 3
    AGENT_TIMEOUT_SECONDS: int = 30
    
    def validate(self) -> bool:
        """
        Validate that required API keys are present.
        Returns True if valid, raises ValueError if not.
        """
        if not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required in .env file")
        
        if not self.NEWS_API_KEY:
            raise ValueError("NEWS_API_KEY is required in .env file")
        
        return True

# Create global settings instance
settings = Settings()

# Validate settings on import
try:
    settings.validate()
    print("Configuration loaded successfully")
except ValueError as e:
    print(f"Configuration error: {e}")
    raise