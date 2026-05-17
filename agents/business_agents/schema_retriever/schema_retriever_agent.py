"""
Agent 2: Schema Retriever
Uses embeddings and keyword matching to find relevant tables/columns for the query.
"""

import sqlite3
from typing import Dict, List, Any, Tuple
from difflib import SequenceMatcher


class SchemaRetrieverAgent:
    def __init__(self, db_path: str = "business_db.sqlite"):
        self.db_path = db_path
        self.schema_cache: Dict[str, Any] = {}
        self.table_embeddings: Dict[str, List[float]] = {}
        self.column_embeddings: Dict[str, List[float]] = {}
        self._load_schema()
    
    def _load_schema(self):
        """Load database schema into memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        # Get schema for each table
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            
            column_info = []
            for col in columns:
                column_info.append({
                    "cid": col[0],
                    "name": col[1],
                    "type": col[2],
                    "notnull": col[3],
                    "default_value": col[4],
                    "pk": col[5]
                })
            
            # Get sample data for better understanding
            cursor.execute(f"SELECT * FROM {table} LIMIT 3")
            samples = cursor.fetchall()
            
            self.schema_cache[table] = {
                "columns": column_info,
                "column_names": [col["name"] for col in column_info],
                "samples": samples,
                "description": self._generate_table_description(table, column_info)
            }
        
        conn.close()
    
    def _generate_table_description(self, table_name: str, columns: List[Dict]) -> str:
        """Generate a natural language description of the table"""
        descriptions = {
            "customers": "Customer information including names, contact details, and loyalty points",
            "employees": "Employee records with positions, departments, and salaries",
            "hotels": "Hotel properties with locations, ratings, and amenities",
            "room_types": "Different types of hotel rooms with pricing and capacity",
            "hotel_rooms": "Individual hotel room instances linked to hotels and room types",
            "hotel_bookings": "Hotel reservation records with check-in/out dates and amounts",
            "hotel_services": "Additional services offered by hotels like spa, room service",
            "hotel_service_usage": "Records of customers using hotel services",
            "restaurants": "Restaurant information with cuisine types and ratings",
            "menu_categories": "Categories for organizing menu items",
            "menu_items": "Food and drink items available at restaurants",
            "restaurant_reservations": "Table reservations at restaurants",
            "restaurant_orders": "Orders placed at restaurants",
            "order_details": "Individual items within restaurant orders",
            "car_categories": "Categories of rental cars with pricing",
            "cars": "Individual vehicles available for rent",
            "car_rentals": "Car rental transactions with dates and costs",
            "insurance_options": "Insurance products available for car rentals",
            "rental_insurance": "Insurance purchased with car rentals",
            "car_additional_services": "Extra services for car rentals like GPS, child seats",
            "rental_additional_services": "Additional services purchased with rentals",
            "payments": "Payment transactions across all business types",
            "reviews": "Customer reviews and ratings for businesses"
        }
        return descriptions.get(table_name, f"Table containing {', '.join([c['name'] for c in columns[:5]])}")
    
    def _keyword_match_score(self, query: str, text: str) -> float:
        """Calculate keyword match score between query and text"""
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        
        if not query_words or not text_words:
            return 0.0
        
        matches = query_words.intersection(text_words)
        return len(matches) / len(query_words)
    
    def _semantic_similarity(self, query: str, text: str) -> float:
        """Calculate semantic similarity using sequence matching (simplified embedding)"""
        return SequenceMatcher(None, query.lower(), text.lower()).ratio()
    
    def retrieve_relevant_tables(self, structured_query: Dict[str, Any], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find most relevant tables based on the structured query
        Returns list of tables with relevance scores and reasons
        """
        business_type = structured_query.get("business_type")
        intent = structured_query.get("intent", "data_retrieval")
        aggregation = structured_query.get("aggregation")
        filters = structured_query.get("filters", {})
        
        table_scores: Dict[str, float] = {}
        table_reasons: Dict[str, List[str]] = {}
        
        # Business type matching
        business_keywords = {
            "hotel": ["hotel", "room", "booking", "reservation", "lodging", "accommodation", "guest", "check-in", "check-out", "night", "stay"],
            "restaurant": ["restaurant", "food", "menu", "order", "dining", "meal", "dish", "vegetarian", "vegan", "salad", "pizza", "burger", "pasta", "recipe", "chef", "table", "waiter", "hungry", "eat", "lunch", "dinner", "breakfast"],
            "car_rental": ["car", "rental", "vehicle", "auto", "drive", "automobile", "taxi", "uber", "lyft", "rent", "lease"]
        }
        
        for table_name, table_info in self.schema_cache.items():
            score = 0.0
            reasons = []
            
            # Match by business type
            if business_type and business_type in business_keywords:
                keywords = business_keywords[business_type]
                desc_match = self._keyword_match_score(" ".join(keywords), table_info["description"])
                name_match = max([self._keyword_match_score(kw, table_name) for kw in keywords])
                
                business_score = max(desc_match, name_match)
                if business_score > 0.3:
                    score += business_score * 2.0
                    reasons.append(f"Matches business type: {business_type}")
            
            # Match by table purpose
            if aggregation:
                if "amount" in table_name or "payment" in table_name or "cost" in table_name or "price" in table_name:
                    score += 1.5
                    reasons.append("Contains monetary values for aggregation")
                elif "count" in aggregation.lower() and any(x in table_name for x in ["booking", "reservation", "order", "rental"]):
                    score += 1.5
                    reasons.append("Transaction table suitable for counting")
            
            # Match by filter fields
            for filter_key, filter_value in filters.items():
                for col_name in table_info["column_names"]:
                    if filter_key.lower() in col_name.lower():
                        score += 1.0
                        reasons.append(f"Has filter column: {col_name}")
                        break
            
            # Check for common query patterns
            if "timeframe" in structured_query and structured_query["timeframe"]:
                date_columns = [c for c in table_info["column_names"] if "date" in c.lower() or "time" in c.lower()]
                if date_columns:
                    score += 0.8
                    reasons.append(f"Has date columns: {', '.join(date_columns)}")
            
            # Boost core transaction tables
            if table_name in ["hotel_bookings", "restaurant_orders", "car_rentals", "payments"]:
                score += 0.5
                reasons.append("Core transaction table")
            
            # Boost customer-related tables for customer queries
            if "customer" in structured_query.get("original", "").lower():
                if table_name == "customers":
                    score += 2.0
                    reasons.append("Direct customer information")
                elif "customer_id" in table_info["column_names"]:
                    score += 0.5
                    reasons.append("Links to customers")
            
            if score > 0:
                table_scores[table_name] = score
                table_reasons[table_name] = reasons
        
        # Sort by score
        sorted_tables = sorted(table_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Build result
        results = []
        for table_name, score in sorted_tables[:top_k]:
            table_info = self.schema_cache[table_name]
            results.append({
                "table_name": table_name,
                "relevance_score": round(score, 2),
                "description": table_info["description"],
                "columns": table_info["column_names"],
                "reasons": table_reasons.get(table_name, ["General relevance"]),
                "sample_data": table_info["samples"][:2] if table_info["samples"] else []
            })
        
        # Ensure minimum tables are returned
        if len(results) < 2:
            # Add related tables based on foreign keys
            core_tables = ["customers", "payments"]
            for table in core_tables:
                if table not in [r["table_name"] for r in results] and table in self.schema_cache:
                    results.append({
                        "table_name": table,
                        "relevance_score": 0.3,
                        "description": self.schema_cache[table]["description"],
                        "columns": self.schema_cache[table]["column_names"],
                        "reasons": ["Related entity table"],
                        "sample_data": self.schema_cache[table]["samples"][:1]
                    })
        
        return results
    
    def get_full_schema(self) -> Dict[str, Any]:
        """Return complete schema information"""
        return self.schema_cache
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get schema for a specific table"""
        return self.schema_cache.get(table_name, {})
    
    def suggest_columns_for_filter(self, table_name: str, filter_type: str) -> List[str]:
        """Suggest columns that might be used for a specific filter type"""
        if table_name not in self.schema_cache:
            return []
        
        columns = self.schema_cache[table_name]["column_names"]
        suggestions = []
        
        filter_patterns = {
            "status": ["status", "state", "condition"],
            "date": ["date", "time", "created", "updated"],
            "amount": ["amount", "price", "cost", "total", "payment"],
            "location": ["city", "country", "address", "location", "region"],
            "customer": ["customer", "client", "guest", "user"]
        }
        
        patterns = filter_patterns.get(filter_type.lower(), [filter_type])
        
        for pattern in patterns:
            for col in columns:
                if pattern.lower() in col.lower():
                    suggestions.append(col)
        
        return list(set(suggestions))


# Example usage
if __name__ == "__main__":
    agent = SchemaRetrieverAgent()
    
    # Test query
    test_query = {
        "original": "Show me hotel bookings for Q1",
        "structured": {
            "intent": "data_retrieval",
            "business_type": "hotel",
            "timeframe": {"label": "q1"},
            "aggregation": None,
            "filters": {}
        }
    }
    
    relevant_tables = agent.retrieve_relevant_tables(test_query["structured"])
    
    print("Relevant Tables:")
    for table in relevant_tables:
        print(f"\n- {table['table_name']} (Score: {table['relevance_score']})")
        print(f"  Description: {table['description']}")
        print(f"  Columns: {', '.join(table['columns'])}")
        print(f"  Reasons: {', '.join(table['reasons'])}")
