# Multi-Agent Text-to-SQL System

A professional, multi-agent architecture for converting natural language queries to SQL with full LLMOps monitoring.

## Architecture

The system uses **4 specialized agents** working together:

1. **Intent Agent** - Analyzes user query to identify intent and relevant tables (dynamically discovered from database)
2. **SQL Agent** - Generates accurate SQL using only the identified tables
3. **Execution Agent** - Safely executes SQL with security validation
4. **Orchestrator Agent** - Coordinates the multi-agent workflow

## Quick Start

### 1. Setup Environment

```bash
cp .env.example .env
# Edit .env with your OpenRouter API key from https://openrouter.ai/keys
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create Database

```bash
python src/utils/setup_db.py
```

Creates 15 tables: customers, restaurants, menu_items, restaurant_orders, order_items, hotels, hotel_bookings, cars, car_rentals, payments, reviews, promotions, customer_promotions, staff, inventory

### 4. Run Application

```bash
streamlit run src/streamlit_ui.py
```

## Example Queries

- "How many vegetarian orders were placed last week?"
- "Show me all hotel bookings this month"
- "What are the top 5 most expensive car rentals?"
- "How many payments failed last week?"

## LLMOps Dashboard

Track success rates, confidence scores, table usage, agent activity, and query history.
