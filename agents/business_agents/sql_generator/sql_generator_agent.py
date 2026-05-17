"""
Agent 4: SQL Generator
Generates correct SQL queries based on approved tables and query context.
Uses the SQLExecutionTool for validation and schema reference.
Includes few-shot examples and dialect specifications for SQLite.
"""

from typing import Dict, List, Any, Optional, Tuple
import re
import sys
import os

# Add tools to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from sql_execution_tool import SQLExecutionTool


class SQLGeneratorAgent:
    def __init__(self, dialect: str = "sqlite", db_path: str = "business_db.sqlite"):
        self.dialect = dialect
        self.db_path = db_path
        self.tool = SQLExecutionTool(db_path)
        self.few_shot_examples = self._load_few_shot_examples()
        self.max_retries = 2
    
    def _load_few_shot_examples(self) -> List[Dict[str, Any]]:
        """Load few-shot examples for SQL generation"""
        return [
            {
                "query": "Show me all hotel bookings",
                "tables": ["hotel_bookings", "customers", "hotel_rooms"],
                "sql": """
                    SELECT 
                        hb.booking_id,
                        c.first_name || ' ' || c.last_name as customer_name,
                        hr.room_number,
                        hb.check_in_date,
                        hb.check_out_date,
                        hb.total_amount,
                        hb.booking_status
                    FROM hotel_bookings hb
                    JOIN customers c ON hb.customer_id = c.customer_id
                    JOIN hotel_rooms hr ON hb.room_id = hr.room_id
                """,
                "explanation": "Basic SELECT with JOINs to get customer names and room numbers"
            },
            {
                "query": "Show total hotel revenue for Q1",
                "tables": ["hotel_bookings"],
                "sql": """
                    SELECT 
                        SUM(total_amount) as total_revenue,
                        COUNT(*) as booking_count
                    FROM hotel_bookings
                    WHERE check_in_date >= date('now', 'start of year')
                      AND check_in_date <= date('now', '+3 months', 'start of year', '-1 day')
                """,
                "explanation": "Aggregation with date filtering for quarter"
            },
            {
                "query": "Show restaurant orders with order details",
                "tables": ["restaurant_orders", "order_details", "menu_items"],
                "sql": """
                    SELECT 
                        ro.order_id,
                        ro.order_date,
                        mi.item_name,
                        od.quantity,
                        od.unit_price,
                        od.total_price
                    FROM restaurant_orders ro
                    JOIN order_details od ON ro.order_id = od.order_id
                    JOIN menu_items mi ON od.item_id = mi.item_id
                """,
                "explanation": "Three-table JOIN for order details with items"
            },
            {
                "query": "Count car rentals by status",
                "tables": ["car_rentals"],
                "sql": """
                    SELECT 
                        status,
                        COUNT(*) as rental_count
                    FROM car_rentals
                    GROUP BY status
                """,
                "explanation": "GROUP BY for counting by category"
            },
            {
                "query": "Show confirmed hotel bookings with customer emails",
                "tables": ["hotel_bookings", "customers"],
                "sql": """
                    SELECT 
                        hb.booking_id,
                        c.first_name,
                        c.last_name,
                        c.email,
                        hb.check_in_date,
                        hb.check_out_date,
                        hb.total_amount
                    FROM hotel_bookings hb
                    JOIN customers c ON hb.customer_id = c.customer_id
                    WHERE hb.booking_status = 'confirmed'
                """,
                "explanation": "Filter by status with customer information"
            },
            {
                "query": "Show average restaurant order amount per customer",
                "tables": ["restaurant_orders", "customers"],
                "sql": """
                    SELECT 
                        c.customer_id,
                        c.first_name || ' ' || c.last_name as customer_name,
                        AVG(ro.total_amount) as avg_order_amount,
                        COUNT(ro.order_id) as order_count
                    FROM customers c
                    JOIN restaurant_orders ro ON c.customer_id = ro.customer_id
                    GROUP BY c.customer_id, c.first_name, c.last_name
                    ORDER BY avg_order_amount DESC
                """,
                "explanation": "Aggregation with GROUP BY and ORDER BY"
            },
            {
                "query": "Show car rentals with insurance costs",
                "tables": ["car_rentals", "rental_insurance", "insurance_options"],
                "sql": """
                    SELECT 
                        cr.rental_id,
                        cr.rental_start_date,
                        cr.rental_end_date,
                        cr.rental_cost,
                        ri.total_cost as insurance_cost,
                        io.insurance_name
                    FROM car_rentals cr
                    LEFT JOIN rental_insurance ri ON cr.rental_id = ri.rental_id
                    LEFT JOIN insurance_options io ON ri.insurance_id = io.insurance_id
                """,
                "explanation": "LEFT JOIN to include rentals without insurance"
            },
            {
                "query": "Show top 5 customers by total spending across all businesses",
                "tables": ["payments", "customers"],
                "sql": """
                    SELECT 
                        c.customer_id,
                        c.first_name || ' ' || c.last_name as customer_name,
                        SUM(p.amount) as total_spending,
                        COUNT(p.payment_id) as payment_count
                    FROM customers c
                    JOIN payments p ON c.customer_id = p.customer_id
                    WHERE p.payment_status = 'completed'
                    GROUP BY c.customer_id, c.first_name, c.last_name
                    ORDER BY total_spending DESC
                    LIMIT 5
                """,
                "explanation": "Cross-business aggregation with LIMIT"
            }
        ]
    
    def generate_sql(
        self, 
        query_context: Dict[str, Any], 
        approved_tables: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate SQL query based on context and approved tables.
        Uses tool for schema validation.
        
        Returns SQL string with metadata
        """
        structured = query_context.get("structured", {})
        business_type = structured.get("business_type")
        aggregation = structured.get("aggregation")
        filters = structured.get("filters", {})
        timeframe = structured.get("timeframe")
        
        table_names = [t["table_name"] for t in approved_tables]
        
        # Determine primary table
        primary_table = self._identify_primary_table(table_names, business_type)
        
        # Build SQL components
        select_clause = self._build_select_clause(primary_table, aggregation, approved_tables)
        from_clause = self._build_from_clause(primary_table)
        join_clauses = self._build_join_clauses(primary_table, table_names, approved_tables)
        where_clauses = self._build_where_clauses(filters, timeframe, approved_tables)
        group_by_clause = self._build_group_by_clause(aggregation, approved_tables)
        order_by_clause = self._build_order_by_clause(aggregation)
        limit_clause = ""
        
        # Assemble SQL
        sql_parts = [select_clause, from_clause]
        if join_clauses:
            sql_parts.append(join_clauses)
        if where_clauses:
            sql_parts.append(f"WHERE {where_clauses}")
        if group_by_clause:
            sql_parts.append(group_by_clause)
        if order_by_clause:
            sql_parts.append(order_by_clause)
        if limit_clause:
            sql_parts.append(limit_clause)
        
        sql_query = "\n".join(sql_parts)
        
        # Validate SQL using tool
        validation_result = self.tool._validate_sql(sql_query)
        
        return {
            "sql": sql_query,
            "is_valid": validation_result["is_valid"],
            "error_message": validation_result.get("error"),
            "primary_table": primary_table,
            "tables_used": table_names,
            "aggregation": aggregation,
            "filters_applied": filters,
            "timeframe_applied": timeframe
        }
    
    def _identify_primary_table(self, table_names: List[str], business_type: Optional[str]) -> str:
        """Identify the primary table for the query"""
        # Priority order for different business types
        priority_tables = {
            "hotel": ["hotel_bookings", "hotel_rooms", "hotels", "customers"],
            "restaurant": ["restaurant_orders", "restaurant_reservations", "restaurants", "customers"],
            "car_rental": ["car_rentals", "cars", "customers"],
            None: ["payments", "customers"]
        }
        
        priorities = priority_tables.get(business_type, priority_tables[None])
        
        for table in priorities:
            if table in table_names:
                return table
        
        # Return first transaction-type table found
        for table in table_names:
            if any(x in table for x in ["booking", "order", "rental", "payment"]):
                return table
        
        return table_names[0] if table_names else "customers"
    
    def _build_select_clause(
        self, 
        primary_table: str, 
        aggregation: Optional[str],
        approved_tables: List[Dict[str, Any]]
    ) -> str:
        """Build SELECT clause based on aggregation and tables"""
        
        # Get columns from primary table
        primary_table_info = next(
            (t for t in approved_tables if t["table_name"] == primary_table), 
            {}
        )
        columns = primary_table_info.get("columns", [])
        
        if aggregation:
            # Aggregation queries
            if aggregation.upper() == "COUNT":
                return f"SELECT COUNT(*) as record_count"
            elif aggregation.upper() == "SUM":
                # Find amount/cost column
                amount_col = next(
                    (c for c in columns if any(x in c.lower() for x in ["amount", "cost", "price", "total"])),
                    "total_amount"
                )
                return f"SELECT SUM({amount_col}) as total_sum"
            elif aggregation.upper() == "AVG":
                amount_col = next(
                    (c for c in columns if any(x in c.lower() for x in ["amount", "cost", "price", "total"])),
                    "total_amount"
                )
                return f"SELECT AVG({amount_col}) as average_value"
            elif aggregation.upper() == "MAX":
                amount_col = next(
                    (c for c in columns if any(x in c.lower() for x in ["amount", "cost", "price", "total"])),
                    "total_amount"
                )
                return f"SELECT MAX({amount_col}) as maximum_value"
            elif aggregation.upper() == "MIN":
                amount_col = next(
                    (c for c in columns if any(x in c.lower() for x in ["amount", "cost", "price", "total"])),
                    "total_amount"
                )
                return f"SELECT MIN({amount_col}) as minimum_value"
        
        # Non-aggregation: select relevant columns
        alias = primary_table.split("_")[0][0] if "_" in primary_table else primary_table[0]
        alias = primary_table[:3]  # Simple alias
        
        select_columns = []
        
        # Add ID column
        id_col = next((c for c in columns if c.endswith("_id")), None)
        if id_col:
            select_columns.append(f"{alias}.{id_col}")
        
        # Add date columns
        date_cols = [c for c in columns if "date" in c.lower()]
        for col in date_cols[:2]:
            select_columns.append(f"{alias}.{col}")
        
        # Add amount columns
        amount_cols = [c for c in columns if any(x in c.lower() for x in ["amount", "cost", "price", "total"])]
        for col in amount_cols[:2]:
            select_columns.append(f"{alias}.{col}")
        
        # Add status column
        status_col = next((c for c in columns if "status" in c.lower()), None)
        if status_col:
            select_columns.append(f"{alias}.{status_col}")
        
        # If no specific columns found, select all
        if not select_columns:
            select_columns = [f"{alias}.*"]
        
        return f"SELECT {', '.join(select_columns)}"
    
    def _build_from_clause(self, primary_table: str) -> str:
        """Build FROM clause with table alias"""
        alias = primary_table[:3]
        return f"FROM {primary_table} {alias}"
    
    def _build_join_clauses(
        self, 
        primary_table: str, 
        table_names: List[str], 
        approved_tables: List[Dict[str, Any]]
    ) -> str:
        """Build JOIN clauses for related tables"""
        joins = []
        
        # Define common join relationships
        join_relationships = {
            "hotel_bookings": [
                ("customers", "customer_id", "customer_id"),
                ("hotel_rooms", "room_id", "room_id")
            ],
            "hotel_rooms": [
                ("hotels", "hotel_id", "hotel_id"),
                ("room_types", "room_type_id", "room_type_id")
            ],
            "restaurant_orders": [
                ("customers", "customer_id", "customer_id"),
                ("restaurant_reservations", "reservation_id", "reservation_id"),
                ("order_details", "order_id", "order_id")
            ],
            "order_details": [
                ("menu_items", "item_id", "item_id")
            ],
            "car_rentals": [
                ("customers", "customer_id", "customer_id"),
                ("cars", "car_id", "car_id"),
                ("employees", "employee_id", "employee_id")
            ],
            "rental_insurance": [
                ("insurance_options", "insurance_id", "insurance_id")
            ],
            "payments": [
                ("customers", "customer_id", "customer_id")
            ],
            "reviews": [
                ("customers", "customer_id", "customer_id")
            ]
        }
        
        # Track used aliases to avoid duplicates
        used_aliases = {primary_table[:3]}
        
        if primary_table in join_relationships:
            for related_table, from_col, to_col in join_relationships[primary_table]:
                if related_table in table_names:
                    # Generate unique alias
                    base_alias = related_table[:3]
                    alias = base_alias
                    counter = 1
                    while alias in used_aliases:
                        alias = base_alias + str(counter)
                        counter += 1
                    used_aliases.add(alias)
                    
                    joins.append(f"JOIN {related_table} {alias} ON {primary_table[:3]}.{from_col} = {alias}.{to_col}")
        
        return "\n".join(joins)
    
    def _build_where_clauses(
        self, 
        filters: Dict[str, Any], 
        timeframe: Optional[Dict[str, Any]],
        approved_tables: List[Dict[str, Any]]
    ) -> str:
        """Build WHERE clause with filters and timeframe"""
        conditions = []
        
        # Add status filters
        if "status" in filters:
            # Find status column in tables
            for table in approved_tables:
                status_col = next((c for c in table["columns"] if "status" in c.lower()), None)
                if status_col:
                    alias = table["table_name"][:3]
                    conditions.append(f"{alias}.{status_col} = '{filters['status']}'")
                    break
        
        # Add timeframe filters
        if timeframe:
            start_date = timeframe.get("start")
            end_date = timeframe.get("end")
            
            if start_date and end_date:
                # Find date column
                for table in approved_tables:
                    date_cols = [c for c in table["columns"] if "date" in c.lower()]
                    if date_cols:
                        alias = table["table_name"][:3]
                        date_col = date_cols[0]
                        conditions.append(f"{alias}.{date_col} >= {start_date}")
                        conditions.append(f"{alias}.{date_col} <= {end_date}")
                        break
        
        return " AND ".join(conditions)
    
    def _build_group_by_clause(
        self, 
        aggregation: Optional[str],
        approved_tables: List[Dict[str, Any]]
    ) -> str:
        """Build GROUP BY clause if needed"""
        if not aggregation:
            return ""
        
        # For aggregations, might want to group by certain dimensions
        # This is simplified - in practice would analyze query intent more
        return ""
    
    def _build_order_by_clause(self, aggregation: Optional[str]) -> str:
        """Build ORDER BY clause"""
        if aggregation:
            return "ORDER BY total_sum DESC" if aggregation.upper() == "SUM" else ""
        return ""
    
    def _validate_sql(self, sql: str) -> Tuple[bool, Optional[str]]:
        """Basic SQL validation"""
        # Check for balanced parentheses
        if sql.count("(") != sql.count(")"):
            return False, "Unbalanced parentheses"
        
        # Check for required keywords
        if "SELECT" not in sql.upper():
            return False, "Missing SELECT keyword"
        
        if "FROM" not in sql.upper():
            return False, "Missing FROM keyword"
        
        # Check for common syntax errors
        if re.search(r',\s*FROM', sql, re.IGNORECASE):
            return False, "Comma before FROM clause"
        
        if re.search(r',\s*WHERE', sql, re.IGNORECASE):
            return False, "Comma before WHERE clause"
        
        return True, None
    
    def retry_with_correction(
        self, 
        sql_result: Dict[str, Any], 
        error_message: str,
        query_context: Dict[str, Any],
        approved_tables: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Attempt to correct SQL based on error"""
        # In a real implementation, this would use LLM to fix the query
        # For now, return basic correction attempt
        sql = sql_result["sql"]
        
        # Common corrections
        if "Unbalanced parentheses" in error_message:
            # Try to balance parentheses
            open_count = sql.count("(")
            close_count = sql.count(")")
            if open_count > close_count:
                sql += ")" * (open_count - close_count)
            elif close_count > open_count:
                sql = "(" * (close_count - open_count) + sql
        
        is_valid, new_error = self._validate_sql(sql)
        
        return {
            "sql": sql,
            "is_valid": is_valid,
            "error_message": new_error,
            "attempted_correction": True
        }
    
    def get_explanation(self, sql: str, query_context: Dict[str, Any]) -> str:
        """Generate natural language explanation of the SQL query"""
        structured = query_context.get("structured", {})
        
        parts = []
        
        if structured.get("aggregation"):
            parts.append(f"This query calculates the {structured['aggregation']} of values")
        else:
            parts.append("This query retrieves records")
        
        if structured.get("business_type"):
            parts.append(f"for {structured['business_type'].replace('_', ' ')}")
        
        if structured.get("filters"):
            filter_desc = ", ".join([f"{k}={v}" for k, v in structured["filters"].items()])
            parts.append(f"filtered by {filter_desc}")
        
        if structured.get("timeframe"):
            parts.append(f"during {structured['timeframe'].get('label', 'the specified period')}")
        
        return ". ".join(parts) + "."


# Example usage
if __name__ == "__main__":
    agent = SQLGeneratorAgent()
    
    # Test case
    query_context = {
        "original": "Show total hotel bookings for Q1",
        "structured": {
            "intent": "data_retrieval",
            "business_type": "hotel",
            "aggregation": "COUNT",
            "timeframe": {"label": "q1", "start": "date('now', 'start of year')", "end": "date('now', '+3 months', 'start of year', '-1 day')"},
            "filters": {}
        }
    }
    
    approved_tables = [
        {"table_name": "hotel_bookings", "columns": ["booking_id", "customer_id", "room_id", "check_in_date", "check_out_date", "total_amount", "booking_status"]},
        {"table_name": "customers", "columns": ["customer_id", "first_name", "last_name", "email"]}
    ]
    
    result = agent.generate_sql(query_context, approved_tables)
    
    print("Generated SQL:")
    print(result["sql"])
    print(f"\nValid: {result['is_valid']}")
    print(f"Explanation: {agent.get_explanation(result['sql'], query_context)}")
