"""
Main Orchestrator for Text-to-SQL Pipeline
Coordinates all 5 agents to process user queries end-to-end.
Supports multi-turn conversations with context management.
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from business_agents.query_parser.query_rewriter_agent import QueryRewriterAgent
from business_agents.schema_retriever.schema_retriever_agent import SchemaRetrieverAgent
from business_agents.hitl_validator.hitl_validator_agent import HITLValidatorAgent
from business_agents.sql_generator.sql_generator_agent import SQLGeneratorAgent
from business_agents.result_formatter.result_formatter_agent import ResultFormatterAgent


class TextToSQLPipeline:
    """
    Main pipeline orchestrating all agents for text-to-SQL conversion
    """
    
    def __init__(self, db_path: str = "business_db.sqlite", auto_approve_timeout: int = 5):
        # Initialize all agents
        self.query_rewriter = QueryRewriterAgent()
        self.schema_retriever = SchemaRetrieverAgent(db_path)
        self.hitl_validator = HITLValidatorAgent(auto_approve_timeout)
        self.sql_generator = SQLGeneratorAgent()
        self.result_formatter = ResultFormatterAgent(db_path)
        
        self.pipeline_history: List[Dict[str, Any]] = []
        self.db_path = db_path
    
    def process_query(self, user_query: str, use_context: bool = True, interactive: bool = True) -> Dict[str, Any]:
        """
        Process user query through entire pipeline
        
        Args:
            user_query: Natural language query from user
            use_context: Whether to use conversation history
            interactive: Whether to wait for user approval of tables
        
        Returns:
            Complete pipeline result with all intermediate steps
        """
        print("\n" + "="*70)
        print("🚀 TEXT-TO-SQL PIPELINE")
        print("="*70)
        print(f"\nUser Query: {user_query}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        pipeline_result = {
            "timestamp": datetime.now().isoformat(),
            "original_query": user_query,
            "steps": {},
            "final_result": None
        }
        
        # Step 1: Query Rewriting & Intent Parsing
        print("\n" + "-"*70)
        print("📝 STEP 1: Query Rewriter & Intent Parser")
        print("-"*70)
        
        rewritten_query = self.query_rewriter.rewrite_query(user_query, use_context=use_context)
        pipeline_result["steps"]["query_rewrite"] = rewritten_query
        
        print(f"Original: {rewritten_query['original']}")
        print(f"Rewritten: {rewritten_query['rewritten_text']}")
        print(f"Business Type: {rewritten_query['structured'].get('business_type', 'N/A')}")
        print(f"Aggregation: {rewritten_query['structured'].get('aggregation', 'N/A')}")
        timeframe = rewritten_query['structured'].get('timeframe')
        print(f"Timeframe: {timeframe.get('label', 'N/A') if timeframe else 'N/A'}")
        print(f"Filters: {rewritten_query['structured'].get('filters', {})}")
        
        # Step 2: Schema Retrieval
        print("\n" + "-"*70)
        print("🔍 STEP 2: Schema Retriever")
        print("-"*70)
        
        relevant_tables = self.schema_retriever.retrieve_relevant_tables(
            rewritten_query["structured"],
            top_k=5
        )
        pipeline_result["steps"]["schema_retrieval"] = relevant_tables
        
        print(f"Found {len(relevant_tables)} relevant tables:")
        for table in relevant_tables:
            print(f"  • {table['table_name']} (Score: {table['relevance_score']})")
            print(f"    Columns: {', '.join(table['columns'][:5])}")
        
        # Step 3: HITL Validation (Table Approval)
        print("\n" + "-"*70)
        print("✅ STEP 3: Human-In-The-Loop Validation")
        print("-"*70)
        
        if interactive:
            # Present tables for approval
            self.hitl_validator.present_tables_for_approval(
                relevant_tables,
                rewritten_query
            )
            
            # Wait for user approval
            approval_result = self.hitl_validator.wait_for_approval_interactive()
            
            if not approval_result.get("approved"):
                print("\n❌ Table selection rejected by user")
                pipeline_result["steps"]["hitl_approval"] = approval_result
                pipeline_result["final_result"] = {
                    "success": False,
                    "error": "User rejected table selection",
                    "message": "Please rephrase your query or try again"
                }
                return pipeline_result
            
            approved_tables = approval_result["tables"]
            approval_method = approval_result.get("method", "unknown")
        else:
            # Auto-approve without user interaction
            approved_tables = relevant_tables
            approval_result = {"approved": True, "method": "auto_skip"}
            approval_method = "auto_skip"
            print("⏭️ Skipping interactive approval (non-interactive mode)")
        
        pipeline_result["steps"]["hitl_approval"] = approval_result
        
        print(f"\nApproval Method: {approval_method}")
        print(f"Approved Tables: {[t['table_name'] for t in approved_tables]}")
        
        # Step 4: SQL Generation
        print("\n" + "-"*70)
        print("💻 STEP 4: SQL Generator")
        print("-"*70)
        
        sql_result = self.sql_generator.generate_sql(
            rewritten_query,
            approved_tables
        )
        pipeline_result["steps"]["sql_generation"] = sql_result
        
        print(f"Primary Table: {sql_result['primary_table']}")
        print(f"Tables Used: {sql_result['tables_used']}")
        print(f"\nGenerated SQL:\n{sql_result['sql']}")
        print(f"\nValid: {sql_result['is_valid']}")
        
        if not sql_result["is_valid"]:
            print(f"Error: {sql_result.get('error_message', 'Unknown error')}")
            
            # Attempt correction
            if sql_result.get("error_message"):
                corrected = self.sql_generator.retry_with_correction(
                    sql_result,
                    sql_result["error_message"],
                    rewritten_query,
                    approved_tables
                )
                if corrected["is_valid"]:
                    print(f"\n✅ Corrected SQL:\n{corrected['sql']}")
                    sql_result = corrected
        
        # Step 5: Execution & Result Formatting
        print("\n" + "-"*70)
        print("📊 STEP 5: Validator, Executor & Result Formatter")
        print("-"*70)
        
        final_result = self.result_formatter.execute_and_format(
            sql_result,
            rewritten_query
        )
        pipeline_result["final_result"] = final_result
        
        if final_result.get("success"):
            print(f"\n✅ Query Executed Successfully!")
            print(f"\nSummary: {final_result.get('summary', 'N/A')}")
            
            data = final_result.get("data", [])
            if data:
                print(f"\nResults ({len(data)} rows):")
                print(json.dumps(data, indent=2))
            
            # Visualization suggestion
            viz_suggestion = self.result_formatter.create_visualization_suggestion(
                data,
                final_result.get("metadata", {}).get("columns", []),
                rewritten_query
            )
            print(f"\n📈 Suggested Visualization: {viz_suggestion.get('recommended_chart', 'N/A')}")
            print(f"   Reason: {viz_suggestion.get('reason', 'N/A')}")
        else:
            print(f"\n❌ Query Execution Failed")
            print(f"Error: {final_result.get('error', 'Unknown error')}")
            if final_result.get("suggestion"):
                print(f"Suggestion: {final_result['suggestion']}")
        
        # Store in pipeline history
        self.pipeline_history.append(pipeline_result)
        
        print("\n" + "="*70)
        print("✅ PIPELINE COMPLETE")
        print("="*70)
        
        return pipeline_result
    
    def get_conversation_summary(self) -> str:
        """Get summary of current conversation context"""
        return self.query_rewriter.get_conversation_summary()
    
    def clear_context(self):
        """Clear all conversation and pipeline history"""
        self.query_rewriter.clear_context()
        self.pipeline_history = []
        print("🗑️ Context cleared")
    
    def run_interactive_session(self):
        """Run interactive CLI session with multi-turn support"""
        print("\n" + "="*70)
        print("🤖 TEXT-TO-SQL INTERACTIVE SESSION")
        print("="*70)
        print("\nWelcome! You can ask questions about:")
        print("  🏨 Hotels (bookings, rooms, revenue)")
        print("  🍽️  Restaurants (orders, menu, reservations)")
        print("  🚗 Car Rentals (rentals, vehicles, insurance)")
        print("  💳 Payments & Reviews across all businesses")
        print("\nCommands:")
        print("  'clear' - Clear conversation context")
        print("  'history' - Show conversation history")
        print("  'quit' or 'exit' - End session")
        print("  'context' - Show current context")
        print("\nExample queries:")
        print("  - 'Show me hotel bookings for Q1'")
        print("  - 'Now filter by status: confirmed'")
        print("  - 'Count restaurant orders'")
        print("  - 'Show total car rental revenue'")
        print("="*70)
        
        while True:
            try:
                user_input = input("\n❓ Your query: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("\n👋 Goodbye!")
                    break
                
                if user_input.lower() == "clear":
                    self.clear_context()
                    continue
                
                if user_input.lower() == "history":
                    print("\n📜 Conversation History:")
                    for i, record in enumerate(self.query_rewriter.conversation_history, 1):
                        print(f"  {i}. {record['original_query']}")
                    continue
                
                if user_input.lower() == "context":
                    print(f"\n📌 Current Context:")
                    print(self.get_conversation_summary())
                    continue
                
                # Process query through pipeline
                result = self.process_query(
                    user_input,
                    use_context=True,
                    interactive=False  # Set to True for table approval prompts
                )
                
                # Show quick result summary
                if result.get("final_result", {}).get("success"):
                    summary = result["final_result"].get("summary", "")
                    print(f"\n✨ {summary}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("Please try again with a different query.")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Text-to-SQL Pipeline")
    parser.add_argument("--db", default="business_db.sqlite", help="Path to SQLite database")
    parser.add_argument("--timeout", type=int, default=5, help="Auto-approve timeout in seconds")
    parser.add_argument("--interactive", action="store_true", help="Run interactive session")
    parser.add_argument("--query", "-q", type=str, help="Single query to process")
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = TextToSQLPipeline(db_path=args.db, auto_approve_timeout=args.timeout)
    
    if args.interactive or not args.query:
        # Run interactive session
        pipeline.run_interactive_session()
    else:
        # Process single query
        result = pipeline.process_query(args.query, use_context=False, interactive=False)
        
        # Output result
        if result.get("final_result", {}).get("success"):
            print("\n" + "="*70)
            print("FINAL RESULT:")
            print("="*70)
            print(json.dumps(result["final_result"], indent=2, default=str))
        else:
            print(f"\nQuery failed: {result.get('final_result', {}).get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
