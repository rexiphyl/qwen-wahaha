"""Text-to-SQL orchestrator coordinating intent recognition and SQL generation."""
import sqlite3
import json
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

from src.core.config import Config
from src.core.llm_client import OpenRouterClient
from src.agents.intent_recognizer import IntentRecognizer


class TextToSQLOrchestrator:
    """Orchestrates the text-to-SQL pipeline with LLMOps tracking."""
    
    def __init__(self):
        self.llm_client = OpenRouterClient()
        self.intent_recognizer = IntentRecognizer()
        self.db_path = str(Config.DB_PATH_FULL)
        self.metrics_log = []
    
    def execute_query(self, question: str) -> Dict[str, Any]:
        """
        Execute the full text-to-SQL pipeline.
        
        Args:
            question: Natural language question
            
        Returns:
            Dictionary with query results and metadata
        """
        start_time = datetime.now()
        
        # Step 1: Intent Recognition
        intent_result = self.intent_recognizer.recognize_intent(question)
        
        # Step 2: Generate SQL using LLM
        llm_result = self.llm_client.generate_sql(
            question=question,
            schema_context=intent_result["schema_context"]
        )
        
        # Step 3: Execute SQL if generation was successful
        sql = llm_result.get("sql", "")
        execution_result = {"success": False, "data": [], "error": None}
        
        if sql and llm_result["success"]:
            execution_result = self._execute_sql(sql)
        
        # Step 4: Compile metrics for LLMOps
        end_time = datetime.now()
        total_latency_ms = int((end_time - start_time).total_seconds() * 1000)
        
        result = {
            "question": question,
            "intent": {
                "keywords": intent_result["detected_keywords"],
                "tables": intent_result["refined_tables"],
                "confidence": intent_result["confidence"]
            },
            "sql": sql,
            "llm_metrics": {
                "success": llm_result["success"],
                "input_tokens": llm_result.get("input_tokens", 0),
                "output_tokens": llm_result.get("output_tokens", 0),
                "total_tokens": llm_result.get("total_tokens", 0),
                "model": llm_result.get("model", ""),
                "llm_latency_ms": llm_result.get("latency_ms", 0),
                "error": llm_result.get("error")
            },
            "execution": execution_result,
            "total_latency_ms": total_latency_ms,
            "timestamp": start_time.isoformat(),
            "status": "success" if execution_result["success"] else "failed"
        }
        
        # Log metrics for LLMOps
        self._log_metrics(result)
        
        return result
    
    def _execute_sql(self, sql: str) -> Dict[str, Any]:
        """Execute SQL query against the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Safety: Only allow SELECT statements
            if not sql.strip().upper().startswith("SELECT"):
                return {
                    "success": False,
                    "data": [],
                    "error": "Only SELECT statements are allowed"
                }
            
            cursor.execute(sql)
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description] if cursor.description else []
            
            # Convert to list of dictionaries
            data = [dict(row) for row in rows]
            
            conn.close()
            
            return {
                "success": True,
                "data": data,
                "row_count": len(data),
                "columns": columns,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"SQL execution error: {e}")
            return {
                "success": False,
                "data": [],
                "error": str(e)
            }
    
    def _log_metrics(self, result: Dict[str, Any]):
        """Log metrics for LLMOps tracking."""
        self.metrics_log.append(result)
        
        # In production, this would write to a file or database
        logger.info(f"Query processed: status={result['status']}, tokens={result['llm_metrics']['total_tokens']}, latency={result['total_latency_ms']}ms")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of metrics for LLMOps dashboard."""
        if not self.metrics_log:
            return {
                "total_queries": 0,
                "successful_queries": 0,
                "failed_queries": 0,
                "avg_latency_ms": 0,
                "total_tokens": 0,
                "avg_tokens_per_query": 0,
                "success_rate": 0,
                "recent_queries": []
            }
        
        total = len(self.metrics_log)
        successful = sum(1 for m in self.metrics_log if m["status"] == "success")
        total_tokens = sum(m["llm_metrics"]["total_tokens"] for m in self.metrics_log)
        total_latency = sum(m["total_latency_ms"] for m in self.metrics_log)
        
        return {
            "total_queries": total,
            "successful_queries": successful,
            "failed_queries": total - successful,
            "avg_latency_ms": round(total_latency / total, 2) if total > 0 else 0,
            "total_tokens": total_tokens,
            "avg_tokens_per_query": round(total_tokens / total, 2) if total > 0 else 0,
            "success_rate": round((successful / total) * 100, 2) if total > 0 else 0,
            "recent_queries": self.metrics_log[-10:]  # Last 10 queries
        }
