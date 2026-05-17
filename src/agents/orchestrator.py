"""
Orchestrator Agent - Coordinates multiple agents to process user queries
Manages the multi-agent workflow and handles retries
"""
from typing import Dict, Any
from loguru import logger
from src.core.config import Config, AgentState
from src.core.llm_client import LLMClient
from src.agents.intent_agent import IntentAgent
from src.agents.sql_agent import SQLAgent
from src.agents.execution_agent import ExecutionAgent

class OrchestratorAgent:
    """
    Main orchestrator that coordinates the multi-agent system.
    Manages workflow: Intent -> SQL Generation -> Execution
    Implements retry logic and error handling.
    """
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.intent_agent = IntentAgent(self.llm_client)
        self.sql_agent = SQLAgent(self.llm_client)
        self.execution_agent = ExecutionAgent()
        logger.info("Orchestrator Agent initialized with multi-agent pipeline")
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Process a user query through the multi-agent pipeline.
        Returns comprehensive result including all agent logs.
        """
        
        logger.info(f"Orchestrator received query: {user_query}")
        
        # Initialize shared state
        state = AgentState(user_query=user_query)
        
        try:
            # Stage 1: Intent Recognition
            logger.info("Stage 1: Intent Recognition")
            state = self.intent_agent.analyze(state)
            
            if state.error_message:
                return self._build_response(state, success=False)
            
            if state.confidence_score < Config.CONFIDENCE_THRESHOLD:
                logger.warning(f"Low confidence in intent: {state.confidence_score}")
                # Continue anyway but note the low confidence
            
            # Stage 2: SQL Generation
            logger.info("Stage 2: SQL Generation")
            state = self.sql_agent.generate(state)
            
            if state.error_message:
                return self._build_response(state, success=False)
            
            # Stage 3: Query Execution
            logger.info("Stage 3: Query Execution")
            state = self.execution_agent.execute(state)
            
            if state.error_message:
                return self._build_response(state, success=False)
            
            logger.info("Query processing completed successfully")
            return self._build_response(state, success=True)
            
        except Exception as e:
            logger.error(f"Orchestrator error: {str(e)}")
            state.error_message = f"System error: {str(e)}"
            return self._build_response(state, success=False)
    
    def _build_response(self, state: AgentState, success: bool) -> Dict[str, Any]:
        """Build comprehensive response dictionary"""
        
        return {
            "success": success,
            "query": state.user_query,
            "intent": state.identified_intent,
            "relevant_tables": state.relevant_tables,
            "sql": state.generated_sql,
            "result": state.execution_result,
            "error": state.error_message,
            "confidence": state.confidence_score,
            "agent_logs": state.agent_history,
            "metadata": {
                "total_agents": len(state.agent_history),
                "database": Config.DATABASE_PATH,
                "model": Config.MODEL_NAME
            }
        }
