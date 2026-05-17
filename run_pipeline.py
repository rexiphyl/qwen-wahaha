#!/usr/bin/env python3
"""
Simple runner for Text-to-SQL Pipeline
Usage: python run_pipeline.py "your query here"
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.business_agents.orchestrator import TextToSQLOrchestrator

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_pipeline.py \"your query here\"")
        print("\nExample queries:")
        print('  python run_pipeline.py "How many hotel bookings do we have?"')
        print('  python run_pipeline.py "Show restaurant orders"')
        print('  python run_pipeline.py "Total car rental revenue"')
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    
    # Initialize orchestrator
    orchestrator = TextToSQLOrchestrator(db_path="business_db.sqlite", auto_approve_timeout=5, interactive=False)
    
    # Step 1: Rewrite query
    print(f"\n📝 Processing query: {query}")
    rewritten = orchestrator.rewrite_query(query)
    print(f"   Intent: {rewritten.get('structured', {}).get('business_type', 'unknown')}")
    
    # Step 2: Retrieve schema
    schema_result = orchestrator.retrieve_schema(query)
    tables = schema_result.get('tables', [])
    table_names = [t['table_name'] for t in tables]
    print(f"   Found tables: {', '.join(table_names)}")
    
    # Step 4: Generate SQL
    sql_result = orchestrator.generate_sql(query, table_names[:3])  # Use top 3 tables
    print(f"   Generated SQL: {sql_result.get('sql', 'N/A')}")
    
    # Step 5: Execute
    final_result = orchestrator.execute_and_format(sql_result.get('sql', ''))
    
    # Show result
    if final_result.get("success"):
        print(f"\n✅ {final_result.get('natural_language', 'Query executed successfully')}")
        if final_result.get('data'):
            print(f"   Data: {final_result['data']}")
    else:
        print(f"\n❌ Error: {final_result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
