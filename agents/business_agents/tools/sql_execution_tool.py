"""
SQL Execution Tool
Provides a unified interface for agents to execute SQL queries safely.
This tool is used by SQL Generator and Result Formatter agents.
"""

import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json


class SQLExecutionTool:
    """
    Tool for executing SQL queries against the business database.
    Provides validation, execution, and error handling capabilities.
    """
    
    def __init__(self, db_path: str = "business_db.sqlite"):
        self.db_path = db_path
        self.allowed_operations = ["SELECT"]
        self.blocked_operations = ["DROP", "DELETE", "TRUNCATE", "ALTER", "INSERT", "UPDATE", "CREATE", "REPLACE"]
    
    def execute_query(
        self, 
        sql: str, 
        params: Optional[Tuple] = None,
        fetch_all: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a SQL query with safety checks.
        
        Args:
            sql: SQL query string
            params: Optional parameters for parameterized queries
            fetch_all: Whether to fetch all rows or just one
            
        Returns:
            Dictionary with success status, data, columns, and metadata
        """
        # Validate SQL
        validation = self._validate_sql(sql)
        if not validation["is_valid"]:
            return {
                "success": False,
                "error": validation["error"],
                "sql": sql,
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Execute query
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            # Get columns
            columns = [description[0] for description in cursor.description] if cursor.description else []
            
            # Fetch results
            if fetch_all:
                rows = cursor.fetchall()
            else:
                rows = cursor.fetchone()
            
            # Convert Row objects to dictionaries
            if rows:
                if isinstance(rows, sqlite3.Row):
                    data = [dict(rows)]
                else:
                    data = [dict(row) for row in rows]
            else:
                data = []
            
            conn.close()
            
            return {
                "success": True,
                "data": data,
                "columns": columns,
                "row_count": len(data) if isinstance(data, list) else 1,
                "sql": sql,
                "timestamp": datetime.now().isoformat()
            }
            
        except sqlite3.Error as e:
            return {
                "success": False,
                "error": f"Database Error: {str(e)}",
                "sql": sql,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected Error: {str(e)}",
                "sql": sql,
                "timestamp": datetime.now().isoformat()
            }
    
    def _validate_sql(self, sql: str) -> Dict[str, Any]:
        """
        Validate SQL query for safety and syntax.
        
        Args:
            sql: SQL query string
            
        Returns:
            Dictionary with validation result and error message if any
        """
        sql_upper = sql.upper().strip()
        
        # Check if query starts with allowed operation
        starts_with_allowed = any(sql_upper.startswith(op) for op in self.allowed_operations)
        if not starts_with_allowed:
            return {
                "is_valid": False,
                "error": f"Query must start with one of: {', '.join(self.allowed_operations)}"
            }
        
        # Check for blocked operations anywhere in query
        for blocked_op in self.blocked_operations:
            if blocked_op in sql_upper:
                # Allow these words if they're not the main operation
                if sql_upper.startswith(blocked_op):
                    return {
                        "is_valid": False,
                        "error": f"Dangerous operation detected: {blocked_op}"
                    }
        
        # Check for balanced parentheses
        if sql.count("(") != sql.count(")"):
            return {
                "is_valid": False,
                "error": "Unbalanced parentheses in SQL query"
            }
        
        # Check for semicolon at end (multiple statements)
        if sql.strip().endswith(";") and sql.count(";") > 1:
            return {
                "is_valid": False,
                "error": "Multiple statements detected. Only single SELECT allowed."
            }
        
        # Basic syntax check - must have FROM clause for SELECT
        if sql_upper.startswith("SELECT") and "FROM" not in sql_upper:
            return {
                "is_valid": False,
                "error": "SELECT query missing FROM clause"
            }
        
        return {"is_valid": True, "error": None}
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """
        Get schema information for a specific table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary with column names, types, and constraints
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Get foreign keys
            cursor.execute(f"PRAGMA foreign_key_list({table_name})")
            foreign_keys = cursor.fetchall()
            
            conn.close()
            
            column_info = []
            for col in columns:
                column_info.append({
                    "cid": col[0],
                    "name": col[1],
                    "type": col[2],
                    "notnull": bool(col[3]),
                    "default_value": col[4],
                    "pk": bool(col[5])
                })
            
            fk_info = []
            for fk in foreign_keys:
                fk_info.append({
                    "id": fk[0],
                    "seq": fk[1],
                    "table": fk[2],
                    "from": fk[3],
                    "to": fk[4]
                })
            
            return {
                "success": True,
                "table_name": table_name,
                "columns": column_info,
                "foreign_keys": fk_info
            }
            
        except sqlite3.Error as e:
            return {
                "success": False,
                "error": f"Error getting schema: {str(e)}",
                "table_name": table_name
            }
    
    def get_all_tables(self) -> Dict[str, Any]:
        """
        Get list of all tables in the database.
        
        Returns:
            Dictionary with list of table names
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT name 
                FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            return {
                "success": True,
                "tables": tables,
                "count": len(tables)
            }
            
        except sqlite3.Error as e:
            return {
                "success": False,
                "error": f"Error getting tables: {str(e)}"
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test database connection.
        
        Returns:
            Dictionary with connection status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            conn.close()
            
            return {
                "success": True,
                "message": "Database connection successful",
                "db_path": self.db_path
            }
            
        except sqlite3.Error as e:
            return {
                "success": False,
                "error": f"Connection failed: {str(e)}",
                "db_path": self.db_path
            }


# Example usage
if __name__ == "__main__":
    tool = SQLExecutionTool()
    
    print("="*60)
    print("SQL EXECUTION TOOL TEST")
    print("="*60)
    
    # Test connection
    print("\n1. Testing connection...")
    result = tool.test_connection()
    print(f"   Status: {'✓' if result['success'] else '✗'} {result.get('message', result.get('error'))}")
    
    # Get all tables
    print("\n2. Getting all tables...")
    result = tool.get_all_tables()
    if result["success"]:
        print(f"   Found {result['count']} tables:")
        for table in result["tables"][:5]:
            print(f"      - {table}")
        if result["count"] > 5:
            print(f"      ... and {result['count'] - 5} more")
    
    # Get schema for a table
    print("\n3. Getting schema for 'customers' table...")
    result = tool.get_table_schema("customers")
    if result["success"]:
        print(f"   Columns ({len(result['columns'])}):")
        for col in result["columns"][:3]:
            print(f"      - {col['name']} ({col['type']})")
        if len(result["columns"]) > 3:
            print(f"      ... and {len(result['columns']) - 3} more")
    
    # Execute a query
    print("\n4. Executing sample query...")
    sql = "SELECT customer_id, first_name, last_name, email FROM customers LIMIT 3"
    result = tool.execute_query(sql)
    if result["success"]:
        print(f"   Query executed successfully!")
        print(f"   Rows returned: {result['row_count']}")
        for row in result["data"]:
            print(f"      - {row['first_name']} {row['last_name']} ({row['email']})")
    
    # Test blocked operation
    print("\n5. Testing blocked operation (DELETE)...")
    sql = "DELETE FROM customers WHERE customer_id = 1"
    result = tool.execute_query(sql)
    print(f"   Status: {'✗ Blocked' if not result['success'] else '✓ Executed'}")
    print(f"   Message: {result.get('error', 'Query executed')}")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
