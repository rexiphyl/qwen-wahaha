# Agent Tool Architecture

## Overview

The business agents system has been refactored to use a **tool-based architecture** where specialized tools provide reusable functionality that multiple agents can leverage. This separation of concerns makes the code more maintainable, testable, and extensible.

## Tools vs Agents

### Tools
Tools are **stateless utilities** that provide specific capabilities:
- **SQLExecutionTool**: Safe SQL query execution with validation
- **SchemaDiscoveryTool**: Database schema introspection and search

Tools:
- Have no knowledge of the agent pipeline
- Can be used independently or by multiple agents
- Provide low-level operations (execute query, get schema, etc.)
- Handle technical concerns (validation, error handling, retries)

### Agents
Agents are **intelligent components** that orchestrate tools to accomplish tasks:
- **Query Rewriter Agent**: Parses user intent
- **Schema Retriever Agent**: Uses SchemaDiscoveryTool to find tables
- **HITL Validator Agent**: Manages user approval workflow
- **SQL Generator Agent**: Uses SQLExecutionTool for validation
- **Result Formatter Agent**: Uses SQLExecutionTool for execution

Agents:
- Understand the pipeline context
- Make decisions based on query intent
- Coordinate multiple tools if needed
- Handle business logic and flow control

## Tool Usage Map

```
┌─────────────────────────────────────────────────────────────┐
│                      TOOLS LAYER                            │
├─────────────────────────────────────────────────────────────┤
│  SQLExecutionTool              SchemaDiscoveryTool          │
│  - execute_query()             - get_all_tables_with_metadata()
│  - _validate_sql()             - find_relevant_tables()     │
│  - get_table_schema()          - get_table_relationships()  │
│  - get_all_tables()            - search_columns_by_pattern()│
│  - test_connection()           - get_sample_data()          │
└─────────────────────────────────────────────────────────────┘
                              ↑
                              │ Used by
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     AGENTS LAYER                            │
├─────────────────────────────────────────────────────────────┤
│  Schema Retriever Agent                                     │
│    → Uses SchemaDiscoveryTool.find_relevant_tables()        │
│    → Uses SchemaDiscoveryTool.get_table_relationships()     │
│                                                             │
│  SQL Generator Agent                                        │
│    → Uses SQLExecutionTool._validate_sql()                  │
│    → Uses SQLExecutionTool.get_table_schema()               │
│                                                             │
│  Result Formatter Agent                                     │
│    → Uses SQLExecutionTool._validate_sql()                  │
│    → Uses SQLExecutionTool.execute_query()                  │
└─────────────────────────────────────────────────────────────┘
```

## Detailed Tool Responsibilities

### SQLExecutionTool
**Location**: `agents/business_agents/tools/sql_execution_tool.py`

**Purpose**: Centralized SQL execution with safety guarantees

**Key Methods**:
- `execute_query(sql, params, fetch_all)`: Execute SELECT queries safely
- `_validate_sql(sql)`: Check for dangerous operations and syntax errors
- `get_table_schema(table_name)`: Get column definitions and foreign keys
- `get_all_tables()`: List all tables in database
- `test_connection()`: Verify database connectivity

**Safety Features**:
- Only allows SELECT operations
- Blocks DROP, DELETE, UPDATE, INSERT, CREATE, ALTER, TRUNCATE
- Validates balanced parentheses
- Prevents multiple statements in one query

**Used By**:
1. **SQL Generator Agent**: Validates generated SQL before returning
2. **Result Formatter Agent**: Executes queries and catches errors

**Example Usage**:
```python
from agents.business_agents.tools import SQLExecutionTool

tool = SQLExecutionTool("business_db.sqlite")

# Execute a query
result = tool.execute_query("SELECT * FROM customers LIMIT 5")
if result["success"]:
    print(result["data"])  # List of dicts
    print(result["columns"])  # Column names
else:
    print(result["error"])

# Validate without executing
validation = tool._validate_sql("DELETE FROM customers")
print(validation["is_valid"])  # False
print(validation["error"])  # "Query must start with one of: SELECT"
```

### SchemaDiscoveryTool
**Location**: `agents/business_agents/tools/schema_discovery_tool.py`

**Purpose**: Intelligent schema discovery and table relevance scoring

**Key Methods**:
- `get_all_tables_with_metadata()`: Complete schema with columns, types, FKs
- `find_relevant_tables(query, keywords, business_type)`: Score tables by relevance
- `get_table_relationships(table_names)`: Map relationships between tables
- `search_columns_by_pattern(pattern)`: Find columns matching pattern
- `get_sample_data(table_name, limit)`: Preview table data

**Intelligence Features**:
- Keyword matching in table and column names
- Business type awareness (hotel/restaurant/car_rental)
- Relevance scoring algorithm
- Relationship graph construction
- Join path suggestions

**Used By**:
1. **Schema Retriever Agent**: Discovers relevant tables for queries
2. **SQL Generator Agent**: Could use for schema reference (future enhancement)

**Example Usage**:
```python
from agents.business_agents.tools import SchemaDiscoveryTool

tool = SchemaDiscoveryTool("business_db.sqlite")

# Find tables for a query
result = tool.find_relevant_tables(
    query="Show hotel bookings with customer names",
    business_type="hotel"
)
for table in result["relevant_tables"]:
    print(f"{table['table_name']}: score={table['score']}")
# Output:
# hotel_bookings: score=8
# hotels: score=5
# customers: score=3

# Get relationships
rels = tool.get_table_relationships(["hotel_bookings", "customers", "hotel_rooms"])
for rel in rels["relationships"]:
    print(f"{rel['from_table']}.{rel['from_column']} → {rel['to_table']}.{rel['to_column']}")
# Output:
# hotel_bookings.customer_id → customers.customer_id
# hotel_bookings.room_id → hotel_rooms.room_id
```

## Agent Integration Examples

### Schema Retriever Agent Using SchemaDiscoveryTool

```python
class SchemaRetrieverAgent:
    def __init__(self, db_path, schema_doc_path):
        self.tool = SchemaDiscoveryTool(db_path, schema_doc_path)
    
    def retrieve_schema(self, query_context):
        # Use tool to find relevant tables
        result = self.tool.find_relevant_tables(
            query=query_context["original"],
            keywords=query_context["structured"]["keywords"],
            business_type=query_context["structured"]["business_type"]
        )
        
        # Enrich with documentation
        enriched = self._enrich_with_documentation(result["relevant_tables"])
        
        # Get relationships using tool
        table_names = [t["table_name"] for t in enriched]
        relationships = self.tool.get_table_relationships(table_names)
        
        return {
            "tables": enriched,
            "relationships": relationships["relationships"]
        }
```

### SQL Generator Agent Using SQLExecutionTool

```python
class SQLGeneratorAgent:
    def __init__(self, db_path):
        self.tool = SQLExecutionTool(db_path)
    
    def generate_sql(self, query_context, approved_tables):
        # Build SQL query
        sql = self._build_query(query_context, approved_tables)
        
        # Validate using tool
        validation = self.tool._validate_sql(sql)
        
        return {
            "sql": sql,
            "is_valid": validation["is_valid"],
            "error_message": validation.get("error")
        }
```

### Result Formatter Agent Using SQLExecutionTool

```python
class ResultFormatterAgent:
    def __init__(self, db_path):
        self.tool = SQLExecutionTool(db_path)
        self.max_retries = 2
    
    def execute_and_format(self, sql_result, query_context):
        sql = sql_result["sql"]
        
        # Validate using tool
        validation = self.tool._validate_sql(sql)
        if not validation["is_valid"]:
            return {"success": False, "error": validation["error"]}
        
        # Execute with retry using tool
        for attempt in range(self.max_retries):
            result = self.tool.execute_query(sql)
            if result["success"]:
                return self._format_response(result, query_context)
            
            # Try to correct and retry
            sql = self._attempt_correction(sql, result["error"])
        
        return {"success": False, "error": "Max retries exceeded"}
```

## Benefits of Tool-Based Architecture

### 1. Separation of Concerns
- Tools handle technical operations (DB access, validation)
- Agents handle business logic (intent parsing, decision making)

### 2. Reusability
- SQLExecutionTool used by 2 different agents
- SchemaDiscoveryTool could be extended to more agents
- No code duplication

### 3. Testability
- Tools can be unit tested independently
- Mock tools for agent testing
- Clear interfaces and contracts

### 4. Maintainability
- Changes to SQL validation only in one place
- Schema discovery logic centralized
- Easy to add new tools without modifying agents

### 5. Extensibility
- Add new tools (e.g., QueryOptimizerTool, CacheTool)
- Agents can compose multiple tools
- Tools can be swapped or enhanced

## Testing Tools Independently

Both tools include comprehensive test suites that can be run directly:

```bash
# Test SQL Execution Tool
python -m agents.business_agents.tools.sql_execution_tool

# Test Schema Discovery Tool  
python -m agents.business_agents.tools.schema_discovery_tool
```

Each test demonstrates:
- Basic functionality
- Error handling
- Edge cases
- Integration with the database

## Future Enhancements

Potential new tools:
1. **QueryOptimizerTool**: Analyze and optimize generated SQL
2. **CacheTool**: Cache frequent queries and results
3. **AuditTool**: Log all queries for compliance
4. **MigrationTool**: Handle schema versioning
5. **BackupTool**: Database backup and restore

Potential tool enhancements:
1. Add embedding-based semantic search to SchemaDiscoveryTool
2. Add query plan analysis to SQLExecutionTool
3. Add parameterized query support for security
4. Add connection pooling for performance

## Summary

The tool-based architecture provides a clean separation between:
- **What to do** (Agents: parse intent, select tables, generate SQL)
- **How to do it** (Tools: execute queries, discover schema, validate)

This makes the system more robust, maintainable, and ready for production use.
