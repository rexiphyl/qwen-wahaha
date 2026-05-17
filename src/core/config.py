"""Configuration management for the Text-to-SQL system."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration."""
    
    # API Configuration
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    MODEL_NAME = os.getenv("MODEL_NAME", "nvidia/nemotron-3-super-120b-a12b:free")
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    
    # Database Configuration
    DATABASE_PATH = os.getenv("DATABASE_PATH", "business_db.sqlite")
    DB_PATH_FULL = Path(__file__).parent.parent.parent / DATABASE_PATH
    
    # LLMOps Configuration
    LOG_DIR = Path(__file__).parent.parent / "logs"
    METRICS_DIR = Path(__file__).parent.parent / "metrics"
    
    # Ensure directories exist
    LOG_DIR.mkdir(exist_ok=True)
    METRICS_DIR.mkdir(exist_ok=True)
    
    # Model parameters
    TEMPERATURE = 0.1
    MAX_TOKENS = 1000
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY must be set in .env file")
        return True
