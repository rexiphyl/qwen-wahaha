"""
SQL Generation Agent - Creates SQL queries based on intent and schema
NO HARDCODING - Uses dynamically discovered schema
"""
import json
import re
from typing import List, Optional
from loguru import logger
from src.core.config import Config, AgentState
from src.core.llm_client import LLMClient

class SQLAgent:
    """
    Agent responsible for generating accurate SQL queries.
    Only uses tables identified by the Intent Agent.
    """
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        logger.info("SQL Agent initialized")
    
    def generate(self, state: AgentState) -> AgentState:
        """Generate SQL query based on identified intent and tables"""
        
        if not state.relevant_tables:
            state.error_message = "No relevant tables identified. Cannot generate SQL."
            state.add_agent_log(
                agent_name="SQLAgent",
                action="sql_generation_failed",
                details="No relevant tables"
            )
            return state
        
        # Get full schema but focus on relevant tables
        full_schema = Config.get_database_schema()
        
        # Filter schema to only show relevant tables (for context efficiency)
        relevant_schema_parts = []
        for table in state.relevant_tables:
            # Extract this table's schema from full schema
            pattern = f"(Table: {table}.*?)(?=Table: |$)"
            match = re.search(pattern, full_schema, re.DOTALL)
            if match:
                relevant_schema_parts.append(match.group(1))
        
        relevant_schema = "\n".join(relevant_schema_parts) if relevant_schema_parts else full_schema
        
        system_prompt = f"""You are a SQL Generation Agent for a Text-to-SQL system.
Your task is to write a precise SQL query to answer the user's question.

User Intent: {state.identified_intent}
Relevant Tables (provided by Intent Agent): {', '.join(state.relevant_tables)}

Database Schema (relevant tables only):
{relevant_schema}

Rules:
- Write ONLY standard SQLite syntax
- Use SELECT statements only (no INSERT, UPDATE, DELETE, DROP)
- Use proper JOINs if multiple tables are needed
- Handle date filters appropriately (e.g., "last week", "this month")
- For boolean/text filters (e.g., "vegetarian"), use appropriate WHERE clauses
- Return your response as valid JSON with this exact structure:
{{
    "sql": "SELECT ... FROM ...",
    "confidence": 0.0-1.0,
    "reasoning": "explanation of the SQL logic",
    "tables_used": ["table1", "table2"]
}}

IMPORTANT: Only use the tables listed in "Relevant Tables". Do not hallucinate columns."""

        user_message = f"""User Query: {state.user_query}
Intent: {state.identified_intent}
Generate SQL to answer this query using only the provided schema."""

        logger.info(f"SQL Agent generating query for intent: {state.identified_intent}")
        
        response = self.llm.chat(system_prompt, user_message, response_format="json")
        
        try:
            parsed = json.loads(response.content)
            
            sql_query = parsed.get("sql", "")
            
            # Basic validation
            if not sql_query.upper().startswith("SELECT"):
                state.error_message = "Generated SQL is not a SELECT statement"
                state.add_agent_log(
                    agent_name="SQLAgent",
                    action="sql_validation_failed",
                    details="Not a SELECT statement"
                )
                return state
            
            state.generated_sql = sql_query
            state.confidence_score = min(state.confidence_score, parsed.get("confidence", 0.5))
            
            state.add_agent_log(
                agent_name="SQLAgent",
                action="sql_generation",
                details=f"SQL: {sql_query[:100]}..., Confidence: {parsed.get('confidence', 0.5)}"
            )
            
            logger.info(f"SQL generated: {sql_query}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse SQL Agent response: {e}")
            state.error_message = f"SQL generation failed: {e}"
            state.add_agent_log(
                agent_name="SQLAgent",
                action="sql_generation_failed",
                details=str(e)
            )
        
        return state
