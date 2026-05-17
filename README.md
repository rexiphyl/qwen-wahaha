# 🏨 Business Intelligence Text-to-SQL Agent

A multi-agent pipeline that converts natural language questions into SQL queries for hotel, restaurant, and car rental businesses.

## Features

- **5 Specialized Agents** working together:
  1. Query Rewriter - Understands intent and context
  2. Schema Retriever - Finds relevant tables
  3. HITL Validator - User approval with 5s auto-approve
  4. SQL Generator - Creates valid SQL queries
  5. Result Formatter - Executes and explains results

- **Multi-turn Conversations** - Remember context across queries
- **Human-in-the-Loop** - Review and approve table selections
- **Self-Correction** - Automatic retry on SQL errors
- **Beautiful UI** - Streamlit interface with step-by-step visualization

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create a `.env` file:
```bash
GROQ_API_KEY=your_groq_api_key_here
MODEL_NAME=llama-3.1-8b-instant
DATABASE_PATH=business_db.sqlite
```

### 3. Create Database (if not exists)
```bash
python create_database.py
```

### 4. Run the Application

**Option A: Streamlit UI (Recommended)**
```bash
streamlit run agents/business_agents/streamlit_ui.py
```
Then open http://localhost:8501 in your browser

**Option B: Command Line**
```bash
python run_pipeline.py "How many hotel bookings do we have?"
```

**Option C: Interactive Session**
```bash
python -m agents.business_agents.orchestrator --interactive
```

## Example Queries

### Hotel Business
- "How many bookings do we have this month?"
- "Show me available rooms in New York"
- "What's the total revenue from hotels?"
- "Which customers have the most loyalty points?"

### Restaurant Business
- "List all restaurants in Paris"
- "Show menu items under $10"
- "Count reservations for tonight"
- "What are the top-selling dishes?"

### Car Rental Business
- "How many cars are currently rented?"
- "Show available SUVs"
- "Calculate total rental revenue"
- "Which insurance option is most popular?"

### Cross-Business
- "Show all payments made yesterday"
- "Find customers with negative reviews"
- "Total revenue across all businesses"

## Project Structure

```
workspace/
├── business_db.sqlite              # SQLite database
├── create_database.py              # Database creation script
├── run_pipeline.py                 # CLI runner
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables
└── agents/
    └── business_agents/
        ├── orchestrator.py         # Main coordinator
        ├── streamlit_ui.py         # Web interface
        ├── schema_documentation.txt # Table descriptions
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
        └── tools/
            ├── sql_execution_tool.py
            └── schema_discovery_tool.py
```

## Database Schema

The database contains **23 tables** across 5 domains:

### Common Tables (2)
- `customers` - Customer information
- `employees` - Staff records

### Hotel Tables (6)
- `hotels` - Hotel properties
- `room_types` - Room categories
- `hotel_rooms` - Individual rooms
- `hotel_bookings` - Reservations
- `hotel_services` - Available services
- `hotel_service_usage` - Service consumption

### Restaurant Tables (6)
- `restaurants` - Restaurant locations
- `menu_categories` - Food categories
- `menu_items` - Menu offerings
- `restaurant_reservations` - Table bookings
- `restaurant_orders` - Customer orders
- `order_details` - Order line items

### Car Rental Tables (7)
- `car_categories` - Vehicle types
- `cars` - Individual vehicles
- `car_rentals` - Rental agreements
- `insurance_options` - Coverage plans
- `rental_insurance` - Purchased insurance
- `car_additional_services` - Extra services
- `rental_additional_services` - Added services

### Cross-Business Tables (2)
- `payments` - All transactions
- `reviews` - Customer feedback

## Configuration

### Model Settings
Edit `.env` to change the LLM:
```bash
MODEL_NAME=llama-3.1-8b-instant  # Default
# Or try: llama-3.3-70b-versatile, mixtral-8x7b-32768
```

### Timeout Settings
Adjust auto-approval timeout in code:
```python
orchestrator = TextToSQLOrchestrator(auto_approve_timeout=10)  # 10 seconds
```

## License

MIT License - Feel free to use and modify!
