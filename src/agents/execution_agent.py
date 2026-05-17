"""
Execution Agent - Safely executes SQL queries and returns results
"""
import sqlite3
from typing import List, Any, Optional
from loguru import logger
from src.core.config import Config, AgentState

class ExecutionAgent:
    """
    Agent responsible for safely executing SQL queries against the database.
    Implements security checks to prevent malicious queries.
    """
    
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
        logger.info("Execution Agent initialized")
    
    def execute(self, state: AgentState) -> AgentState:
        """Execute the generated SQL query and capture results"""
        
        if not state.generated_sql:
            state.error_message = "No SQL query to execute"
            state.add_agent_log(
                agent_name="ExecutionAgent",
                action="execution_failed",
                details="No SQL query"
            )
            return state
        
        # Security validation
        sql_upper = state.generated_sql.upper().strip()
        
        forbidden_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER", "TRUNCATE"]
        for keyword in forbidden_keywords:
            if keyword in sql_upper:
                state.error_message = f"Security violation: {keyword} statements are not allowed"
                state.add_agent_log(
                    agent_name="ExecutionAgent",
                    action="security_block",
                    details=f"Blocked {keyword} statement"
                )
                logger.warning(f"Blocked dangerous SQL: {state.generated_sql}")
                return state
        
        if not sql_upper.startswith("SELECT"):
            state.error_message = "Only SELECT statements are allowed"
            state.add_agent_log(
                agent_name="ExecutionAgent",
                action="security_block",
                details="Not a SELECT statement"
            )
            return state
        
        try:
            logger.info(f"Executing SQL: {state.generated_sql}")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(state.generated_sql)
            
            # Get column names
            columns = [description[0] for description in cursor.description]
            
            # Fetch results
            results = cursor.fetchall()
            
            conn.close()
            
            state.execution_result = {
                "columns": columns,
                "rows": results,
                "count": len(results)
            }
            
            state.add_agent_log(
                agent_name="ExecutionAgent",
                action="execution_success",
                details=f"Executed successfully, {len(results)} rows returned"
            )
            
            logger.info(f"Query executed successfully: {len(results)} rows returned")
            
        except sqlite3.Error as e:
            logger.error(f"Database error: {str(e)}")
            state.error_message = f"Database error: {str(e)}"
            state.add_agent_log(
                agent_name="ExecutionAgent",
                action="execution_failed",
                details=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error during execution: {str(e)}")
            state.error_message = f"Execution error: {str(e)}"
            state.add_agent_log(
                agent_name="ExecutionAgent",
                action="execution_failed",
                details=str(e)
            )
        
        return state
