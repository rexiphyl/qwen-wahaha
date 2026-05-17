"""
Agent 5: Result Formatter & NL Response
Executes SQL using the SQLExecutionTool, validates results, handles errors with self-correction,
and formats output with natural language responses.
"""

import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
import sys
import os

# Add tools to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from sql_execution_tool import SQLExecutionTool


class ResultFormatterAgent:
    def __init__(self, db_path: str = "business_db.sqlite"):
        self.db_path = db_path
        self.tool = SQLExecutionTool(db_path)
        self.max_retries = 2
    
    def execute_and_format(
        self, 
        sql_result: Dict[str, Any], 
        query_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute SQL query using tool and format results with natural language response
        Includes validation and self-correction loop
        """
        sql_query = sql_result.get("sql", "")
        
        # Step 1: Validate SQL syntax using tool
        validation_result = self.tool._validate_sql(sql_query)
        if not validation_result["is_valid"]:
            return {
                "success": False,
                "error": f"SQL Validation Error: {validation_result['error']}",
                "query": sql_query,
                "suggestion": "Please check the SQL syntax"
            }
        
        # Step 2: Execute with retry logic using tool
        execution_result = self._execute_with_retry(sql_query, sql_result, query_context)
        
        if not execution_result["success"]:
            return execution_result
        
        # Step 3: Format results
        formatted_response = self._format_response(
            execution_result["data"],
            execution_result["columns"],
            query_context,
            sql_query
        )
        
        return formatted_response
    
    def _execute_with_retry(
        self, 
        sql: str, 
        sql_result: Dict[str, Any],
        query_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute SQL with retry mechanism for error correction using the tool"""
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            # Use tool to execute query
            result = self.tool.execute_query(sql)
            
            if result["success"]:
                return {
                    "success": True,
                    "data": result["data"],
                    "columns": result["columns"],
                    "row_count": result["row_count"],
                    "attempt": attempt,
                    "sql_executed": sql
                }
            else:
                last_error = result.get("error", "Unknown error")
                
                if attempt < self.max_retries:
                    # Attempt self-correction
                    corrected_sql = self._attempt_sql_correction(sql, last_error)
                    if corrected_sql != sql:
                        sql = corrected_sql
                        continue
        
        return {
            "success": False,
            "error": f"Database Error: {last_error}",
            "query": sql,
            "attempts": self.max_retries,
            "suggestion": "Try modifying your query or checking table names"
        }
    
    def _attempt_sql_correction(self, sql: str, error_message: str) -> str:
        """Attempt to correct common SQL errors"""
        import re
        corrected = sql
        
        # Common corrections based on error messages
        if "no such table" in error_message.lower():
            # Extract table name from error
            import re
            match = re.search(r"no such table: (\w+)", error_message, re.IGNORECASE)
            if match:
                wrong_table = match.group(1)
                # Suggest similar tables (in real implementation would use schema)
                pass
        
        if "ambiguous column name" in error_message.lower():
            # Add table aliases to ambiguous columns
            match = re.search(r"column (.+) is ambiguous", error_message, re.IGNORECASE)
            if match:
                ambiguous_col = match.group(1)
                # This is simplified - real implementation would parse SQL properly
                pass
        
        if "near" in error_message.lower() and "syntax error" in error_message.lower():
            # Try to fix common syntax issues
            # Remove trailing commas
            corrected = re.sub(r',\s*(WHERE|GROUP|ORDER|LIMIT|$)', r' \1', corrected)
        
        return corrected
    
    def _format_response(
        self, 
        data: List[Tuple], 
        columns: List[str], 
        query_context: Dict[str, Any],
        sql_query: str
    ) -> Dict[str, Any]:
        """Format query results with natural language response"""
        
        row_count = len(data)
        structured = query_context.get("structured", {})
        aggregation = structured.get("aggregation")
        
        # Generate natural language summary
        summary = self._generate_summary(row_count, aggregation, structured, query_context.get("original", ""))
        
        # Format data for display
        formatted_data = self._format_data_for_display(data, columns, aggregation)
        
        # Build response
        response = {
            "success": True,
            "summary": summary,
            "data": formatted_data,
            "metadata": {
                "row_count": row_count,
                "columns": columns,
                "sql_executed": sql_query,
                "execution_time": datetime.now().isoformat(),
                "query_context": {
                    "original": query_context.get("original"),
                    "business_type": structured.get("business_type"),
                    "aggregation": aggregation
                }
            }
        }
        
        return response
    
    def _generate_summary(
        self, 
        row_count: int, 
        aggregation: Optional[str],
        structured: Dict[str, Any],
        original_query: str
    ) -> str:
        """Generate natural language summary of results"""
        
        business_type = structured.get("business_type", "business")
        
        if aggregation:
            agg_type = aggregation.upper()
            
            if row_count > 0 and len(str(row_count)) > 0:
                if agg_type == "COUNT":
                    return f"Found {row_count} records matching your query for {business_type.replace('_', ' ')}."
                elif agg_type in ["SUM", "AVG", "MAX", "MIN"]:
                    # Value will be in the data
                    return f"Calculated {agg_type} value for {business_type.replace('_', ' ')}."
            
            return f"Aggregation ({agg_type}) completed for {business_type.replace('_', ' ')}."
        
        else:
            if row_count == 0:
                return f"No records found matching your criteria for {business_type.replace('_', ' ')}."
            elif row_count == 1:
                return f"Found 1 record matching your query."
            elif row_count <= 10:
                return f"Found {row_count} records matching your query for {business_type.replace('_', ' ')}."
            else:
                return f"Found {row_count} records. Showing all results for {business_type.replace('_', ' ')}."
    
    def _format_data_for_display(
        self, 
        data: List[Tuple], 
        columns: List[str],
        aggregation: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Format data as list of dictionaries for easy consumption"""
        
        if not data or not columns:
            return []
        
        # For aggregation queries with single result
        if aggregation and len(data) == 1 and len(columns) <= 2:
            result = {}
            for i, col in enumerate(columns):
                value = data[0][i]
                if isinstance(value, float):
                    value = round(value, 2)
                result[col] = value
            return [result]
        
        # Regular formatting
        formatted = []
        for row in data[:50]:  # Limit to 50 rows for display
            row_dict = {}
            for i, col in enumerate(columns):
                value = row[i]
                # Format specific types
                if isinstance(value, float):
                    value = round(value, 2)
                row_dict[col] = value
            formatted.append(row_dict)
        
        return formatted
    
    def create_visualization_suggestion(
        self, 
        data: List[Dict[str, Any]], 
        columns: List[str],
        query_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Suggest appropriate visualization for the data"""
        
        structured = query_context.get("structured", {})
        aggregation = structured.get("aggregation")
        
        suggestion = {
            "recommended_chart": None,
            "reason": None,
            "config": {}
        }
        
        if aggregation:
            if aggregation.upper() == "COUNT":
                suggestion["recommended_chart"] = "bar_chart"
                suggestion["reason"] = "Count data is best visualized with bars"
            elif aggregation.upper() in ["SUM", "AVG"]:
                suggestion["recommended_chart"] = "metric_card"
                suggestion["reason"] = "Single aggregate value displayed as metric"
        elif len(data) > 0:
            # Check for date columns
            date_cols = [c for c in columns if "date" in c.lower()]
            amount_cols = [c for c in columns if any(x in c.lower() for x in ["amount", "cost", "price", "total"])]
            
            if date_cols and amount_cols:
                suggestion["recommended_chart"] = "line_chart"
                suggestion["reason"] = "Time series data with amounts"
                suggestion["config"] = {"x_axis": date_cols[0], "y_axis": amount_cols[0]}
            elif len(data) <= 10:
                suggestion["recommended_chart"] = "table"
                suggestion["reason"] = "Small dataset suitable for tabular display"
            else:
                suggestion["recommended_chart"] = "paginated_table"
                suggestion["reason"] = "Large dataset requires pagination"
        
        return suggestion
    
    def export_results(
        self, 
        data: List[Dict[str, Any]], 
        format_type: str = "json"
    ) -> str:
        """Export results in different formats"""
        
        if format_type.lower() == "json":
            return json.dumps(data, indent=2, default=str)
        elif format_type.lower() == "csv":
            if not data:
                return ""
            
            headers = list(data[0].keys())
            csv_lines = [",".join(headers)]
            
            for row in data:
                values = [str(row.get(h, "")) for h in headers]
                csv_lines.append(",".join(values))
            
            return "\n".join(csv_lines)
        
        return json.dumps(data, indent=2, default=str)


# Example usage
if __name__ == "__main__":
    agent = ResultFormatterAgent()
    
    # Test case
    query_context = {
        "original": "Show total hotel bookings count",
        "structured": {
            "business_type": "hotel",
            "aggregation": "COUNT"
        }
    }
    
    sql_result = {
        "sql": "SELECT COUNT(*) as record_count FROM hotel_bookings",
        "is_valid": True
    }
    
    result = agent.execute_and_format(sql_result, query_context)
    
    print("="*60)
    print("QUERY RESULT:")
    print("="*60)
    print(f"\nSummary: {result.get('summary', 'N/A')}")
    print(f"\nData: {json.dumps(result.get('data', []), indent=2)}")
    print(f"\nMetadata: {json.dumps(result.get('metadata', {}), indent=2, default=str)}")
    
    if result.get("success"):
        viz_suggestion = agent.create_visualization_suggestion(
            result["data"],
            result["metadata"]["columns"],
            query_context
        )
        print(f"\nVisualization Suggestion: {viz_suggestion}")
