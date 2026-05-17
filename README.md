# Professional Text-to-SQL Agent with LLMOps

A production-ready text-to-SQL system powered by OpenRouter and NVIDIA Nemotron-3 Super, featuring comprehensive intent recognition, 15+ database tables, and a full LLMOps dashboard.

## Features

- **Two-Stage Intent Recognition**: Accurately maps questions to correct database tables
- **15 Database Tables**: Comprehensive schema covering restaurants, hotels, car rentals, payments, and more
- **LLMOps Dashboard**: Real-time monitoring of query performance, token usage, success rates, and latency
- **Professional Architecture**: Modular code structure with proper separation of concerns
- **OpenRouter Integration**: Uses free NVIDIA Nemotron-3 Super 120B model

## Project Structure

```
/workspace
├── src/
│   ├── core/
│   │   ├── config.py          # Configuration management
│   │   ├── llm_client.py      # OpenRouter API client
│   │   └── schema.py          # Database schema definitions
│   ├── agents/
│   │   ├── intent_recognizer.py  # Intent recognition engine
│   │   └── orchestrator.py       # Main orchestration logic
│   ├── llmops/
│   │   └── dashboard.py       # LLMOps visualization
│   ├── utils/
│   │   └── setup_db.py        # Database setup script
│   └── streamlit_ui.py        # Main Streamlit application
├── business_db.sqlite         # SQLite database
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (create from .env.example)
└── .env.example              # Environment template
```

## Setup Instructions

### 1. Create `.env` file

Copy the example environment file and add your OpenRouter API key:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:
```
OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
MODEL_NAME=nvidia/nemotron-3-super-120b-a12b:free
DATABASE_PATH=business_db.sqlite
```

Get your free API key from: https://openrouter.ai/keys

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Database

```bash
python -c "from src.utils.setup_db import setup_database; setup_database()"
```

This creates `business_db.sqlite` with 15 tables and sample data:
- customers, restaurants, menu_items, restaurant_orders, order_items
- hotels, hotel_bookings
- cars, car_rentals
- payments, reviews, promotions, customer_promotions
- staff, inventory

### 4. Run the Application

```bash
streamlit run src/streamlit_ui.py
```

The app will open at http://localhost:8501

## Usage Examples

### Query Interface

Ask natural language questions like:

- **"How many vegetarian orders were placed last week?"** - Queries restaurant Orders with vegetarian items
- **"Show me all hotel bookings this month"** - Shows hotel booking data
- **"What are the top 5 most expensive car rentals?"** - Analyzes car rental costs
- **"How many payments failed last month?"** - Payment analytics
- **"Show me customer reviews with rating below 3"** - Review analysis

### LLMOps Dashboard

Navigate to the LLMOps Dashboard tab to see:
- **Success Rate Over Time**: Track query success percentage
- **Latency Distribution**: Histogram of total and LLM latency
- **Token Usage**: Input/output tokens per query
- **Confidence Scores**: Intent recognition confidence distribution
- **Recent Queries Table**: Last 10 queries with metrics
- **Summary Statistics**: Total queries, success rate, avg latency, avg tokens

### Database Schema

View all 15 tables with descriptions and column information in the Database Schema tab.

## Architecture Highlights

### Intent Recognition Engine

Two-stage process for accurate table mapping:
1. **Keyword Extraction**: Identifies relevant terms (vegetarian, booking, rental, etc.)
2. **Contextual Refinement**: Analyzes question structure to refine table selection

Special handling for:
- Vegetarian/vegan food queries → menu_items, order_items, restaurant_orders
- Time-based queries → Filters to tables with date columns
- Count queries → Targets transaction tables

### LLMOps Tracking

Every query logs:
- Timestamp and latency metrics
- Token consumption (input/output/total)
- Intent recognition confidence
- Target tables identified
- Success/failure status
- Generated SQL

### Security

- Only SELECT statements are executed
- Parameterized queries prevent SQL injection
- API keys managed via environment variables

## Sample Questions by Category

### Restaurant & Food
- How many vegetarian orders were placed last week?
- Show me all vegan menu items
- What's the most popular restaurant by order count?
- Find orders with special instructions

### Hotel Bookings
- How many bookings do I have this month?
- Show checked-in guests at Grand Plaza Hotel
- What's the average booking price by room type?

### Car Rentals
- Which cars are currently available?
- Show overdue rentals
- Calculate total revenue from SUV rentals

### Payments
- How many payments failed last week?
- Show pending payments
- Total payments by method this month

### Cross-Table Queries
- Show customers who ordered vegetarian food and booked hotels
- Find customers with both car rentals and restaurant orders

## Troubleshooting

### ModuleNotFoundError: No module named 'agents'
Ensure you're running from the project root and the `src` directory structure is intact.

### OPENROUTER_API_KEY not configured
Check that your `.env` file exists and contains a valid API key.

### Database not found
Run the setup script: `python -c "from src.utils.setup_db import setup_database; setup_database()"`

### Query returns wrong table results
The intent recognition may need refinement. Check the "Intent Analysis" panel to see which tables were selected.

## Technologies Used

- **Streamlit**: Web UI framework
- **Plotly**: Interactive visualizations
- **Pandas**: Data manipulation
- **Pydantic**: Data validation
- **Loguru**: Logging
- **OpenRouter API**: LLM access
- **SQLite**: Database

## License

MIT License
