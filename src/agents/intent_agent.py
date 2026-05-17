"""
Intent Recognition Agent - Dynamically identifies user intent and relevant tables
NO HARDCODING - Discovers tables from database schema
"""
import json
from typing import List
from loguru import logger
from src.core.config import Config, AgentState, LLMResponse
from src.core.llm_client import LLMClient

class IntentAgent:
    """
    Agent responsible for understanding user intent and identifying relevant tables.
    Dynamically discovers available tables from the database schema.
    """
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        logger.info("Intent Agent initialized")
    
    def analyze(self, state: AgentState) -> AgentState:
        """Analyze user query to identify intent and relevant tables"""
        
        # Get dynamic schema
        schema = Config.get_database_schema()
        
        system_prompt = f"""You are an Intent Recognition Agent for a Text-to-SQL system.
Your task is to analyze the user's question and identify:
1. The user's intent (what they want to know)
2. The relevant database tables needed to answer the question

Available Tables (dynamically discovered from database):
{schema}

Rules:
- ONLY select tables that are actually relevant to the query
- If the query mentions "vegetarian", "food", "orders", "menu", look for restaurant-related tables
- If the query mentions "bookings", "hotel", "rooms", look for hotel-related tables
- If the query mentions "cars", "rental", "vehicles", look for car rental tables
- If the query mentions "payments", "transactions", look for payment tables
- Return your response as valid JSON with this exact structure:
{{
    "intent": "brief description of what user wants",
    "relevant_tables": ["table1", "table2"],
    "confidence": 0.0-1.0,
    "reasoning": "why you chose these tables"
}}

Be precise. Only include tables that contain data needed for the query."""

        user_message = f"User Query: {state.user_query}"
        
        logger.info(f"Intent Agent analyzing: {state.user_query}")
        
        response = self.llm.chat(system_prompt, user_message, response_format="json")
        
        try:
            # Parse JSON response
            parsed = json.loads(response.content)
            
            state.identified_intent = parsed.get("intent", "unknown")
            state.relevant_tables = parsed.get("relevant_tables", [])
            state.confidence_score = parsed.get("confidence", 0.5)
            
            state.add_agent_log(
                agent_name="IntentAgent",
                action="intent_recognition",
                details=f"Intent: {state.identified_intent}, Tables: {state.relevant_tables}, Confidence: {state.confidence_score}"
            )
            
            logger.info(f"Intent identified: {state.identified_intent}")
            logger.info(f"Relevant tables: {state.relevant_tables}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Intent Agent response: {e}")
            state.error_message = f"Intent recognition failed: {e}"
            state.add_agent_log(
                agent_name="IntentAgent",
                action="intent_recognition_failed",
                details=str(e)
            )
        
        return state
