"""
Core Configuration and Base Classes for Multi-Agent Text-to-SQL System
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import sqlite3
import logging
from loguru import logger

# Load environment variables
load_dotenv()

class Config:
    """Centralized configuration management - NO HARDCODING"""
    
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME", "nvidia/nemotron-3-super-120b-a12b:free")
    DATABASE_PATH = os.getenv("DATABASE_PATH", "business_db.sqlite")
    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
    
    # Agent configuration
    MAX_RETRIES = 3
    CONFIDENCE_THRESHOLD = 0.7
    
    @classmethod
    def get_database_schema(cls) -> str:
        """Dynamically fetch database schema from actual database"""
        if not os.path.exists(cls.DATABASE_PATH):
            raise FileNotFoundError(f"Database not found: {cls.DATABASE_PATH}. Run setup_db.py first.")
        
        conn = sqlite3.connect(cls.DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get all tables dynamically
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]
        
        schema_parts = []
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            col_defs = []
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                not_null = "NOT NULL" if col[3] else ""
                col_defs.append(f"  {col_name} {col_type} {not_null}")
            
            # Get sample data for context
            cursor.execute(f"SELECT * FROM {table} LIMIT 3")
            samples = cursor.fetchall()
            sample_str = ", ".join([str(s) for s in samples[0]]) if samples else "No data"
            
            schema_parts.append(f"""
Table: {table}
Columns:
{chr(10).join(col_defs)}
Sample data: {sample_str}
""")
        
        conn.close()
        return "\n".join(schema_parts)

class LLMResponse(BaseModel):
    """Structured LLM response"""
    content: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentState(BaseModel):
    """Shared state between agents"""
    user_query: str
    identified_intent: Optional[str] = None
    relevant_tables: List[str] = Field(default_factory=list)
    generated_sql: Optional[str] = None
    execution_result: Optional[List[Any]] = None
    error_message: Optional[str] = None
    confidence_score: float = 0.0
    agent_history: List[Dict[str, str]] = Field(default_factory=list)
    
    def add_agent_log(self, agent_name: str, action: str, details: str):
        self.agent_history.append({
            "agent": agent_name,
            "action": action,
            "details": details
        })

# Setup logging
logger.add("logs/agent_system.log", rotation="10 MB", level="DEBUG")
