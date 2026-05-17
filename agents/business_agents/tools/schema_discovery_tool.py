"""
Schema Discovery Tool
Provides agents with capabilities to discover and understand database schema.
Used by Schema Retriever agent for table discovery and relationship mapping.
"""

import sqlite3
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import json
import re


class SchemaDiscoveryTool:
    """
    Tool for discovering database schema, tables, columns, and relationships.
    Provides semantic search capabilities for finding relevant tables.
    """
    
    def __init__(self, db_path: str = "business_db.sqlite", schema_doc_path: str = None):
        self.db_path = db_path
        self.schema_doc_path = schema_doc_path
        self._table_cache = {}
        self._relationship_cache = {}
    
    def get_all_tables_with_metadata(self) -> Dict[str, Any]:
        """
        Get all tables with detailed metadata including columns, types, and relationships.
        
        Returns:
            Dictionary with comprehensive table information
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("""
                SELECT name 
                FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            table_names = [row[0] for row in cursor.fetchall()]
            
            tables_info = {}
            for table_name in table_names:
                # Get column info
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                # Get foreign keys
                cursor.execute(f"PRAGMA foreign_key_list({table_name})")
                foreign_keys = cursor.fetchall()
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                
                column_info = []
                for col in columns:
                    column_info.append({
                        "name": col[1],
                        "type": col[2],
                        "notnull": bool(col[3]),
                        "default_value": col[4],
                        "primary_key": bool(col[5])
                    })
                
                fk_info = []
                for fk in foreign_keys:
                    fk_info.append({
                        "reference_table": fk[2],
                        "from_column": fk[3],
                        "to_column": fk[4]
                    })
                
                tables_info[table_name] = {
                    "columns": column_info,
                    "foreign_keys": fk_info,
                    "row_count": row_count,
                    "column_names": [col["name"] for col in column_info]
                }
            
            conn.close()
            
            return {
                "success": True,
                "tables": tables_info,
                "table_names": list(tables_info.keys()),
                "count": len(tables_info),
                "timestamp": datetime.now().isoformat()
            }
            
        except sqlite3.Error as e:
            return {
                "success": False,
                "error": f"Error getting schema: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def find_relevant_tables(
        self, 
        query: str, 
        keywords: Optional[List[str]] = None,
        business_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Find tables relevant to a user query using keyword matching.
        
        Args:
            query: User's natural language query
            keywords: Additional keywords to match
            business_type: Filter by business type (hotel, restaurant, car_rental)
            
        Returns:
            Dictionary with ranked list of relevant tables
        """
        # Get all tables with metadata
        schema_result = self.get_all_tables_with_metadata()
        if not schema_result["success"]:
            return schema_result
        
        # Normalize query
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))
        
        if keywords:
            query_words.update([k.lower() for k in keywords])
        
        # Business type mapping
        business_keywords = {
            "hotel": ["hotel", "room", "booking", "check-in", "check-out", "stay", "night", "reservation"],
            "restaurant": ["restaurant", "order", "menu", "food", "dish", "meal", "dining", "reservation", "table"],
            "car_rental": ["car", "rental", "vehicle", "drive", "automobile", "insurance", "pickup", "return"]
        }
        
        # Common transaction keywords
        transaction_keywords = ["customer", "payment", "review", "employee", "service"]
        
        scored_tables = {}
        
        for table_name, table_info in schema_result["tables"].items():
            score = 0
            matched_keywords = []
            
            # Score based on table name
            table_name_lower = table_name.lower()
            for word in query_words:
                if word in table_name_lower:
                    score += 3
                    matched_keywords.append(f"name:{word}")
            
            # Score based on column names
            for col_name in table_info["column_names"]:
                col_lower = col_name.lower()
                for word in query_words:
                    if word in col_lower:
                        score += 1
                        matched_keywords.append(f"column:{word}")
            
            # Business type filtering/scoring
            if business_type and business_type in business_keywords:
                business_words = business_keywords[business_type]
                # Check table name
                for bw in business_words:
                    if bw in table_name_lower:
                        score += 5
                        matched_keywords.append(f"business:{bw}")
                # Check columns
                for col_name in table_info["column_names"]:
                    for bw in business_words:
                        if bw in col_name.lower():
                            score += 2
            
            # Boost transaction tables for general queries
            if any(tk in table_name_lower for tk in ["booking", "order", "rental", "payment"]):
                if not business_type or any(bw in query_words for bw in transaction_keywords):
                    score += 2
            
            if score > 0:
                scored_tables[table_name] = {
                    "score": score,
                    "matched_keywords": list(set(matched_keywords)),
                    "columns": table_info["columns"],
                    "foreign_keys": table_info["foreign_keys"],
                    "row_count": table_info["row_count"]
                }
        
        # Sort by score descending
        sorted_tables = sorted(
            scored_tables.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )
        
        return {
            "success": True,
            "query": query,
            "business_type": business_type,
            "relevant_tables": [
                {"table_name": name, **info} 
                for name, info in sorted_tables
            ],
            "total_found": len(sorted_tables),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_table_relationships(self, table_names: List[str]) -> Dict[str, Any]:
        """
        Get relationships between specified tables.
        
        Args:
            table_names: List of table names to analyze
            
        Returns:
            Dictionary with relationship graph
        """
        schema_result = self.get_all_tables_with_metadata()
        if not schema_result["success"]:
            return schema_result
        
        relationships = []
        tables_analyzed = set()
        
        for table_name in table_names:
            if table_name not in schema_result["tables"]:
                continue
            
            table_info = schema_result["tables"][table_name]
            
            # Direct foreign keys from this table
            for fk in table_info["foreign_keys"]:
                ref_table = fk["reference_table"]
                if ref_table in table_names or ref_table in schema_result["tables"]:
                    relationships.append({
                        "from_table": table_name,
                        "from_column": fk["from_column"],
                        "to_table": ref_table,
                        "to_column": fk["to_column"],
                        "relationship_type": "many_to_one"
                    })
                    tables_analyzed.add(table_name)
                    tables_analyzed.add(ref_table)
        
        # Build join path suggestions
        join_paths = self._suggest_join_paths(table_names, relationships)
        
        return {
            "success": True,
            "tables_analyzed": list(tables_analyzed),
            "relationships": relationships,
            "join_paths": join_paths,
            "timestamp": datetime.now().isoformat()
        }
    
    def _suggest_join_paths(
        self, 
        table_names: List[str], 
        relationships: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        Suggest optimal join paths between tables.
        
        Args:
            table_names: List of tables to join
            relationships: Known relationships between tables
            
        Returns:
            List of suggested join paths
        """
        if len(table_names) <= 1:
            return []
        
        # Build adjacency graph
        graph = {}
        for table in table_names:
            graph[table] = []
        
        for rel in relationships:
            from_t = rel["from_table"]
            to_t = rel["to_table"]
            
            if from_t in graph and to_t in graph:
                graph[from_t].append({
                    "target": to_t,
                    "on": f"{from_t}.{rel['from_column']} = {to_t}.{rel['to_column']}"
                })
                graph[to_t].append({
                    "target": from_t,
                    "on": f"{to_t}.{rel['to_column']} = {from_t}.{rel['from_column']}"
                })
        
        # Simple BFS to find paths
        paths = []
        start_table = table_names[0]
        visited = {start_table}
        queue = [(start_table, [start_table])]
        
        while queue and len(paths) < 5:
            current, path = queue.pop(0)
            
            for neighbor in graph.get(current, []):
                target = neighbor["target"]
                if target not in visited:
                    visited.add(target)
                    new_path = path + [target]
                    queue.append((target, new_path))
                    
                    if target in table_names:
                        paths.append({
                            "path": new_path,
                            "joins": [
                                graph[new_path[i]][j]["on"] 
                                for i in range(len(new_path)-1)
                                for j, n in enumerate(graph[new_path[i]])
                                if n["target"] == new_path[i+1]
                            ][:len(new_path)-1]
                        })
        
        return paths
    
    def get_sample_data(self, table_name: str, limit: int = 3) -> Dict[str, Any]:
        """
        Get sample data from a table for preview.
        
        Args:
            table_name: Name of the table
            limit: Number of rows to return
            
        Returns:
            Dictionary with sample rows
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(f"SELECT * FROM {table_name} LIMIT ?", (limit,))
            rows = cursor.fetchall()
            
            # Convert to list of dicts
            sample_data = [dict(row) for row in rows]
            
            conn.close()
            
            return {
                "success": True,
                "table_name": table_name,
                "sample_data": sample_data,
                "row_count": len(sample_data),
                "timestamp": datetime.now().isoformat()
            }
            
        except sqlite3.Error as e:
            return {
                "success": False,
                "error": f"Error getting sample data: {str(e)}",
                "table_name": table_name
            }
    
    def search_columns_by_pattern(
        self, 
        pattern: str, 
        case_sensitive: bool = False
    ) -> Dict[str, Any]:
        """
        Search for columns matching a pattern across all tables.
        
        Args:
            pattern: Pattern to search for (supports partial matches)
            case_sensitive: Whether search is case-sensitive
            
        Returns:
            Dictionary with matching columns
        """
        schema_result = self.get_all_tables_with_metadata()
        if not schema_result["success"]:
            return schema_result
        
        matches = []
        search_pattern = pattern if case_sensitive else pattern.lower()
        
        for table_name, table_info in schema_result["tables"].items():
            for col in table_info["columns"]:
                col_name = col["name"] if case_sensitive else col["name"].lower()
                
                if search_pattern in col_name:
                    matches.append({
                        "table_name": table_name,
                        "column_name": col["name"],
                        "column_type": col["type"],
                        "is_primary_key": col["primary_key"],
                        "is_notnull": col["notnull"]
                    })
        
        return {
            "success": True,
            "pattern": pattern,
            "matches": matches,
            "count": len(matches),
            "timestamp": datetime.now().isoformat()
        }


# Example usage
if __name__ == "__main__":
    tool = SchemaDiscoveryTool()
    
    print("="*60)
    print("SCHEMA DISCOVERY TOOL TEST")
    print("="*60)
    
    # Get all tables
    print("\n1. Getting all tables...")
    result = tool.get_all_tables_with_metadata()
    if result["success"]:
        print(f"   Found {result['count']} tables")
        for table in list(result["tables"].keys())[:5]:
            cols = len(result["tables"][table]["columns"])
            print(f"      - {table} ({cols} columns)")
    
    # Find relevant tables
    print("\n2. Finding tables for query: 'Show hotel bookings'...")
    result = tool.find_relevant_tables("Show hotel bookings")
    if result["success"]:
        print(f"   Found {result['total_found']} relevant tables:")
        for t in result["relevant_tables"][:3]:
            print(f"      - {t['table_name']} (score: {t['score']}, matches: {', '.join(t['matched_keywords'])})")
    
    # Get relationships
    print("\n3. Getting relationships for ['hotel_bookings', 'customers', 'hotel_rooms']...")
    result = tool.get_table_relationships(["hotel_bookings", "customers", "hotel_rooms"])
    if result["success"]:
        print(f"   Found {len(result['relationships'])} relationships:")
        for rel in result["relationships"][:3]:
            print(f"      - {rel['from_table']}.{rel['from_column']} → {rel['to_table']}.{rel['to_column']}")
    
    # Get sample data
    print("\n4. Getting sample data from 'customers'...")
    result = tool.get_sample_data("customers", limit=2)
    if result["success"]:
        print(f"   Sample rows:")
        for row in result["sample_data"]:
            print(f"      - {row.get('first_name', 'N/A')} {row.get('last_name', 'N/A')} ({row.get('email', 'N/A')})")
    
    # Search columns
    print("\n5. Searching columns with pattern 'amount'...")
    result = tool.search_columns_by_pattern("amount")
    if result["success"]:
        print(f"   Found {result['count']} columns:")
        for match in result["matches"][:5]:
            print(f"      - {match['table_name']}.{match['column_name']} ({match['column_type']})")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
