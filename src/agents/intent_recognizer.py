"""Intent recognition module for accurate table mapping."""
import re
from typing import List, Dict, Set
from loguru import logger
from src.core.schema import INTENT_KEYWORDS, SCHEMA_METADATA


class IntentRecognizer:
    """Recognize user intent and map to relevant database tables."""
    
    def __init__(self):
        self.keyword_map = INTENT_KEYWORDS
        self.schema_metadata = SCHEMA_METADATA
    
    def extract_keywords(self, question: str) -> List[str]:
        """Extract relevant keywords from the question."""
        question_lower = question.lower()
        found_keywords = []
        
        for keyword in self.keyword_map.keys():
            if keyword in question_lower:
                found_keywords.append(keyword)
        
        # Also check for specific food-related terms
        food_terms = ['vegetarian', 'vegan', 'veg', 'non-veg', 'meat', 'chicken', 'fish', 'seafood']
        for term in food_terms:
            if term in question_lower and term not in found_keywords:
                found_keywords.append(term)
        
        return found_keywords
    
    def get_relevant_tables(self, keywords: List[str]) -> Set[str]:
        """Get set of relevant tables based on keywords."""
        relevant_tables = set()
        
        for keyword in keywords:
            if keyword in self.keyword_map:
                relevant_tables.update(self.keyword_map[keyword])
        
        # If no keywords matched, return all tables as fallback
        if not relevant_tables:
            relevant_tables = set(self.schema_metadata.keys())
        
        return relevant_tables
    
    def recognize_intent(self, question: str) -> Dict:
        """
        Perform two-stage intent recognition.
        
        Stage 1: Keyword-based table identification
        Stage 2: Contextual refinement based on question structure
        
        Returns:
            Dictionary with recognized intent information
        """
        # Stage 1: Extract keywords and get initial table candidates
        keywords = self.extract_keywords(question)
        candidate_tables = self.get_relevant_tables(keywords)
        
        # Stage 2: Refine based on question context
        refined_tables = self._refine_tables(question, candidate_tables)
        
        # Build schema context for LLM
        schema_context = self._build_schema_context(refined_tables)
        
        result = {
            "question": question,
            "detected_keywords": keywords,
            "candidate_tables": list(candidate_tables),
            "refined_tables": list(refined_tables),
            "schema_context": schema_context,
            "confidence": self._calculate_confidence(keywords, question)
        }
        
        logger.info(f"Intent recognized: {result['refined_tables']} with confidence {result['confidence']}")
        return result
    
    def _refine_tables(self, question: str, candidate_tables: Set[str]) -> Set[str]:
        """Refine table selection based on question context."""
        question_lower = question.lower()
        
        # Specific refinements for common query patterns
        if 'vegetarian' in question_lower or 'vegan' in question_lower or 'veg' in question_lower:
            # Prioritize restaurant-related tables
            restaurant_tables = {'menu_items', 'order_items', 'restaurant_orders', 'restaurants'}
            candidate_tables = candidate_tables.intersection(restaurant_tables) or restaurant_tables
        
        elif 'how many' in question_lower or 'count' in question_lower:
            # Count queries usually target main transaction tables
            if 'booking' in question_lower:
                candidate_tables = {'hotel_bookings'}
            elif 'order' in question_lower or 'food' in question_lower:
                candidate_tables = {'restaurant_orders', 'order_items'}
            elif 'rental' in question_lower or 'car' in question_lower:
                candidate_tables = {'car_rentals'}
        
        elif 'last week' in question_lower or 'last month' in question_lower or 'this month' in question_lower:
            # Time-based queries need tables with date columns
            date_tables = {
                'restaurant_orders', 'hotel_bookings', 'car_rentals', 
                'payments', 'reviews'
            }
            candidate_tables = candidate_tables.intersection(date_tables) or candidate_tables
        
        return candidate_tables
    
    def _build_schema_context(self, tables: Set[str]) -> str:
        """Build a concise schema context for the LLM."""
        context_parts = []
        
        for table_name in sorted(tables):
            if table_name in self.schema_metadata:
                meta = self.schema_metadata[table_name]
                columns_str = ", ".join(meta["columns"])
                context_parts.append(f"Table: {table_name}\nDescription: {meta['description']}\nColumns: {columns_str}\n")
        
        return "\n".join(context_parts)
    
    def _calculate_confidence(self, keywords: List[str], question: str) -> float:
        """Calculate confidence score for intent recognition."""
        if not keywords:
            return 0.3
        
        base_confidence = min(0.5 + len(keywords) * 0.15, 0.95)
        
        # Boost confidence for specific patterns
        question_lower = question.lower()
        if any(pattern in question_lower for pattern in ['how many', 'count', 'total']):
            base_confidence = min(base_confidence + 0.1, 0.98)
        
        return round(base_confidence, 2)
