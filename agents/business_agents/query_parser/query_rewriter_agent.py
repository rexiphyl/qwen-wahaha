"""
Agent 1: Query Rewriter & Intent Parser
Handles multi-turn context, rewrites queries with history, and extracts intent.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any

class QueryRewriterAgent:
    def __init__(self):
        self.conversation_history: List[Dict[str, Any]] = []
        self.context_state: Dict[str, Any] = {
            "last_tables": [],
            "last_filters": {},
            "last_timeframe": None,
            "last_business_type": None,
            "aggregation": None,
            "group_by": None,
            "order_by": None,
            "limit": None
        }
    
    def add_to_history(self, user_query: str, rewritten_query: str, metadata: Dict):
        """Add interaction to conversation history"""
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "original_query": user_query,
            "rewritten_query": rewritten_query,
            "metadata": metadata,
            "context_snapshot": self.context_state.copy()
        })
        
        # Keep only last 10 turns to avoid context overflow
        if len(self.conversation_history) > 10:
            self.conversation_history.pop(0)
    
    def detect_intent(self, query: str) -> Dict[str, Any]:
        """Detect user intent from query"""
        query_lower = query.lower()
        
        intent = {
            "type": "data_retrieval",
            "action": "select",
            "entities": [],
            "timeframe": None,
            "filters": {},
            "aggregation": None,
            "business_type": None
        }
        
        # Detect business type
        if any(word in query_lower for word in ["hotel", "room", "booking", "reservation"]):
            intent["business_type"] = "hotel"
        elif any(word in query_lower for word in ["restaurant", "food", "menu", "order", "dining"]):
            intent["business_type"] = "restaurant"
        elif any(word in query_lower for word in ["car", "rental", "vehicle", "auto"]):
            intent["business_type"] = "car_rental"
        
        # Detect timeframes
        time_indicators = {
            "today": ("date('now')", "date('now')"),
            "yesterday": ("date('now', '-1 day')", "date('now', '-1 day')"),
            "this week": ("date('now', 'weekday 0')", "date('now')"),
            "last week": ("date('now', '-7 days')", "date('now', '-7 days')"),
            "this month": ("date('now', 'start of month')", "date('now')"),
            "last month": ("date('now', '-1 month', 'start of month')", "date('now', '-1 month', 'end of month')"),
            "q1": ("date('now', 'start of year')", "date('now', '+3 months', 'start of year', '-1 day')"),
            "q2": ("date('now', 'start of year', '+3 months')", "date('now', 'start of year', '+6 months', '-1 day')"),
            "q3": ("date('now', 'start of year', '+6 months')", "date('now', 'start of year', '+9 months', '-1 day')"),
            "q4": ("date('now', 'start of year', '+9 months')", "date('now', 'end of year')"),
            "this year": ("date('now', 'start of year')", "date('now', 'end of year')"),
            "last year": ("date('now', '-1 year', 'start of year')", "date('now', '-1 year', 'end of year')")
        }
        
        for indicator, (start, end) in time_indicators.items():
            if indicator in query_lower:
                intent["timeframe"] = {"start": start, "end": end, "label": indicator}
                break
        
        # Detect aggregation
        if any(word in query_lower for word in ["total", "sum", "amount"]):
            intent["aggregation"] = "SUM"
        elif any(word in query_lower for word in ["average", "avg"]):
            intent["aggregation"] = "AVG"
        elif any(word in query_lower for word in ["count", "how many"]):
            intent["aggregation"] = "COUNT"
        elif any(word in query_lower for word in ["max", "highest"]):
            intent["aggregation"] = "MAX"
        elif any(word in query_lower for word in ["min", "lowest"]):
            intent["aggregation"] = "MIN"
        
        # Detect filters
        if "region" in query_lower or "west" in query_lower or "east" in query_lower or "north" in query_lower or "south" in query_lower:
            regions = []
            if "west" in query_lower:
                regions.append("West")
            if "east" in query_lower:
                regions.append("East")
            if "north" in query_lower:
                regions.append("North")
            if "south" in query_lower:
                regions.append("South")
            if regions:
                intent["filters"]["region"] = regions
        
        if "status" in query_lower:
            if "confirmed" in query_lower:
                intent["filters"]["status"] = "confirmed"
            elif "cancelled" in query_lower:
                intent["filters"]["status"] = "cancelled"
            elif "active" in query_lower:
                intent["filters"]["status"] = "active"
        
        # Extract entities (simplified NER)
        import re
        # Look for numbers (could be IDs, quantities, etc.)
        numbers = re.findall(r'\b\d+\b', query)
        if numbers:
            intent["entities"].extend([{"type": "number", "value": n} for n in numbers])
        
        return intent
    
    def rewrite_query(self, user_query: str, use_context: bool = True) -> Dict[str, Any]:
        """
        Rewrite query incorporating conversation context
        Returns structured query representation
        """
        # Detect current intent
        current_intent = self.detect_intent(user_query)
        
        # Check for context-dependent queries
        query_lower = user_query.lower()
        
        # Handle follow-up queries
        if use_context and self.conversation_history:
            # Filter refinement
            if "filter" in query_lower or "only" in query_lower or "show" in query_lower:
                # Merge with previous context
                if self.context_state["last_business_type"] and not current_intent["business_type"]:
                    current_intent["business_type"] = self.context_state["last_business_type"]
                
                # Update filters
                for key, value in current_intent["filters"].items():
                    self.context_state["last_filters"][key] = value
                
                # Update timeframe if mentioned
                if current_intent["timeframe"]:
                    self.context_state["last_timeframe"] = current_intent["timeframe"]
            
            # Aggregation change
            if any(word in query_lower for word in ["total", "average", "count", "sum"]):
                if not current_intent["aggregation"]:
                    # Try to infer from query
                    pass
            
            # Apply accumulated context
            if not current_intent["filters"] and self.context_state["last_filters"]:
                current_intent["filters"] = self.context_state["last_filters"].copy()
            
            if not current_intent["timeframe"] and self.context_state["last_timeframe"]:
                current_intent["timeframe"] = self.context_state["last_timeframe"]
        
        # Build rewritten query representation
        rewritten = {
            "original": user_query,
            "rewritten_text": self._generate_natural_language_rewrite(user_query, current_intent),
            "structured": {
                "intent": current_intent["type"],
                "action": current_intent["action"],
                "business_type": current_intent["business_type"] or self.context_state.get("last_business_type"),
                "timeframe": current_intent["timeframe"],
                "filters": {**self.context_state.get("last_filters", {}), **current_intent["filters"]},
                "aggregation": current_intent["aggregation"],
                "entities": current_intent["entities"]
            },
            "context_used": use_context and len(self.conversation_history) > 0
        }
        
        # Update context state
        if current_intent["business_type"]:
            self.context_state["last_business_type"] = current_intent["business_type"]
        if current_intent["filters"]:
            self.context_state["last_filters"].update(current_intent["filters"])
        if current_intent["timeframe"]:
            self.context_state["last_timeframe"] = current_intent["timeframe"]
        if current_intent["aggregation"]:
            self.context_state["aggregation"] = current_intent["aggregation"]
        
        # Add to history
        self.add_to_history(user_query, rewritten["rewritten_text"], current_intent)
        
        return rewritten
    
    def _generate_natural_language_rewrite(self, original: str, intent: Dict) -> str:
        """Generate a clearer version of the query"""
        parts = []
        
        if intent.get("business_type"):
            parts.append(f"[Business: {intent['business_type']}]")
        
        if intent.get("aggregation"):
            parts.append(f"[Aggregation: {intent['aggregation']}]")
        
        if intent.get("timeframe"):
            parts.append(f"[Timeframe: {intent['timeframe'].get('label', 'custom')}]")
        
        if intent.get("filters"):
            filter_str = ", ".join([f"{k}: {v}" for k, v in intent["filters"].items()])
            parts.append(f"[Filters: {filter_str}]")
        
        return f"{original} {' '.join(parts)}" if parts else original
    
    def get_conversation_summary(self) -> str:
        """Get summary of conversation for context"""
        if not self.conversation_history:
            return "No previous conversation."
        
        last_turn = self.conversation_history[-1]
        return f"Last query: {last_turn['original_query']}. Context: Business={self.context_state.get('last_business_type', 'N/A')}, Filters={self.context_state.get('last_filters', {})}"
    
    def clear_context(self):
        """Clear conversation history and context"""
        self.conversation_history = []
        self.context_state = {
            "last_tables": [],
            "last_filters": {},
            "last_timeframe": None,
            "last_business_type": None,
            "aggregation": None,
            "group_by": None,
            "order_by": None,
            "limit": None
        }


# Example usage
if __name__ == "__main__":
    agent = QueryRewriterAgent()
    
    # First query
    result1 = agent.rewrite_query("Show me hotel bookings for Q1")
    print("Query 1:", json.dumps(result1, indent=2))
    
    # Follow-up query
    result2 = agent.rewrite_query("Now filter by status: confirmed")
    print("\nQuery 2:", json.dumps(result2, indent=2))
    
    # Another follow-up
    result3 = agent.rewrite_query("Show total amount instead")
    print("\nQuery 3:", json.dumps(result3, indent=2))
