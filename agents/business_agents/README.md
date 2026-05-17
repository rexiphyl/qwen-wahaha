# Business Agents - Text-to-SQL Pipeline

A multi-agent system for converting natural language queries to SQL, with support for multi-turn conversations and human-in-the-loop validation.

## Architecture

```
User Query 
   ↓
[1] Query Rewriter & Intent Parser
   ↓
[2] Schema Retriever (embeddings + keyword match)
   ↓
[3] HITL UI (optional table/column override, auto-approve after N sec)
   ↓
[4] SQL Generator (prompt + few-shot + dialect spec)
   ↓
[5] Validator & Executor (syntax check → run → catch errors)
   ↓
[6] Self-Correction Loop (max 2 retries on error)
   ↓
[7] Result Formatter & NL Response
```

## Agents

### 1. Query Rewriter Agent (`query_parser/query_rewriter_agent.py`)
- Handles multi-turn context
- Rewrites queries with conversation history
- Extracts intent, business type, timeframes, filters, and aggregations

### 2. Schema Retriever Agent (`schema_retriever/schema_retriever_agent.py`)
- Uses keyword matching and semantic similarity
- Identifies relevant tables and columns
- Provides relevance scores and reasons

### 3. HITL Validator Agent (`hitl_validator/hitl_validator_agent.py`)
- Presents selected tables for user approval
- Auto-approves after configurable timeout (default: 5 seconds)
- Allows user to add/remove tables

### 4. SQL Generator Agent (`sql_generator/sql_generator_agent.py`)
- Generates SQLite-compatible SQL
- Includes few-shot examples
- Supports aggregation, filtering, joins, and timeframes

### 5. Result Formatter Agent (`result_formatter/result_formatter_agent.py`)
- Validates SQL syntax before execution
- Executes with retry mechanism (max 2 retries)
- Formats results with natural language summaries
- Suggests visualizations

## Installation

```bash
# Ensure you have the database created
python create_business_db.py

# Run the pipeline
python -m agents.business_agents.orchestrator --query "Show me hotel bookings"
```

## Usage

### Interactive Mode

```bash
python -m agents.business_agents.orchestrator --interactive
```

### Single Query

```bash
python -m agents.business_agents.orchestrator -q "Count restaurant orders for Q1"
```

### With Custom Database

```bash
python -m agents.business_agents.orchestrator --db /path/to/db.sqlite -q "Show total revenue"
```

## Example Queries

### Hotel Business
- "Show me hotel bookings for Q1"
- "Count confirmed reservations"
- "Show total hotel revenue this month"
- "List all available rooms"

### Restaurant Business
- "Show restaurant orders with details"
- "Count orders by status"
- "Show average order amount per customer"
- "List menu items for French restaurants"

### Car Rental Business
- "Show car rentals this week"
- "Count active rentals"
- "Show total rental revenue"
- "List available SUVs"

### Cross-Business
- "Show top customers by spending"
- "Count payments by method"
- "Show reviews by business type"

### Multi-Turn Examples
```
User: "Show me hotel bookings for Q1"
Assistant: [Shows results]

User: "Now filter by status: confirmed"
Assistant: [Applies filter to previous context]

User: "Show total amount instead"
Assistant: [Changes aggregation to SUM]
```

## Commands in Interactive Mode

| Command | Description |
|---------|-------------|
| `clear` | Clear conversation context |
| `history` | Show conversation history |
| `context` | Show current context state |
| `quit` / `exit` | End session |

## Database Schema

The system works with a SQLite database containing:
- **Common Tables**: customers, employees
- **Hotel Tables**: hotels, room_types, hotel_rooms, hotel_bookings, hotel_services, hotel_service_usage
- **Restaurant Tables**: restaurants, menu_categories, menu_items, restaurant_reservations, restaurant_orders, order_details
- **Car Rental Tables**: car_categories, cars, car_rentals, insurance_options, rental_insurance, car_additional_services, rental_additional_services
- **Cross-Business Tables**: payments, reviews

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--db` | business_db.sqlite | Path to SQLite database |
| `--timeout` | 5 | Auto-approve timeout in seconds |
| `--interactive` | false | Run interactive session |
| `--query` | - | Single query to process |

## Project Structure

```
agents/
└── business_agents/
    ├── query_parser/
    │   └── query_rewriter_agent.py
    ├── schema_retriever/
    │   └── schema_retriever_agent.py
    ├── hitl_validator/
    │   └── hitl_validator_agent.py
    ├── sql_generator/
    │   └── sql_generator_agent.py
    ├── result_formatter/
    │   └── result_formatter_agent.py
    ├── orchestrator.py
    └── __init__.py
```

## Features

✅ **Multi-Turn Context Handling** - Maintains conversation history and state
✅ **Intent Detection** - Identifies business type, aggregations, filters, timeframes
✅ **Schema Discovery** - Automatically discovers and caches database schema
✅ **Human-in-the-Loop** - User can approve/modify table selection
✅ **Auto-Approval** - Tables auto-approved after timeout if no user action
✅ **SQL Generation** - Generates valid SQLite queries with proper joins
✅ **Self-Correction** - Retries with corrections on SQL errors (max 2 retries)
✅ **Natural Language Responses** - Summarizes results in plain English
✅ **Visualization Suggestions** - Recommends appropriate charts for data

## License

MIT
