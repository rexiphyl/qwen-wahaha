"""
Agent 3: HITL Validator (Human-In-The-Loop)
Presents selected tables to user for confirmation with auto-approve timeout.
"""

import time
import threading
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime


class HITLValidatorAgent:
    def __init__(self, auto_approve_timeout: int = 5):
        self.auto_approve_timeout = auto_approve_timeout
        self.pending_approval: Optional[Dict[str, Any]] = None
        self.approval_timer: Optional[threading.Timer] = None
        self.is_approved = False
        self.user_override: Optional[Dict[str, Any]] = None
        self.callback: Optional[Callable] = None
    
    def present_tables_for_approval(
        self, 
        selected_tables: List[Dict[str, Any]], 
        query_context: Dict[str, Any],
        callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Present selected tables to user for approval
        Returns approval status and any modifications
        """
        self.callback = callback
        self.is_approved = False
        self.user_override = None
        
        approval_request = {
            "timestamp": datetime.now().isoformat(),
            "query_context": query_context,
            "selected_tables": selected_tables,
            "status": "pending",
            "auto_approve_in": self.auto_approve_timeout
        }
        
        self.pending_approval = approval_request
        
        # Display tables for user review
        print("\n" + "="*60)
        print("📋 TABLE SELECTION FOR APPROVAL")
        print("="*60)
        print(f"\nQuery: {query_context.get('original', 'N/A')}")
        print(f"\nAuto-approve in: {self.auto_approve_timeout} seconds")
        print("\nSelected Tables:")
        
        for i, table in enumerate(selected_tables, 1):
            print(f"\n{i}. {table['table_name']} (Relevance: {table['relevance_score']})")
            print(f"   Description: {table['description']}")
            print(f"   Columns: {', '.join(table['columns'][:8])}")
            if len(table['columns']) > 8:
                print(f"   ... and {len(table['columns']) - 8} more columns")
            print(f"   Reasons: {', '.join(table['reasons'])}")
        
        print("\n" + "-"*60)
        print("OPTIONS:")
        print("  - Type table names to ADD (comma-separated)")
        print("  - Type 'remove: table_name' to REMOVE a table")
        print("  - Type 'approve' to confirm immediately")
        print("  - Type 'reject' to cancel")
        print("  - Wait for auto-approval")
        print("-"*60)
        
        # Start auto-approve timer
        self.approval_timer = threading.Timer(
            self.auto_approve_timeout, 
            self._auto_approve
        )
        self.approval_timer.start()
        
        return approval_request
    
    def _auto_approve(self):
        """Automatically approve after timeout"""
        if not self.is_approved and self.pending_approval:
            print(f"\n⏰ Auto-approved after {self.auto_approve_timeout} seconds")
            self.is_approved = True
            self.pending_approval["status"] = "auto_approved"
            
            if self.callback:
                self.callback({
                    "approved": True,
                    "tables": self.pending_approval["selected_tables"],
                    "method": "auto"
                })
    
    def get_user_input(self) -> Optional[str]:
        """Get user input with timeout handling"""
        try:
            user_input = input("\nYour choice: ").strip()
            
            # Cancel timer if user responds
            if self.approval_timer:
                self.approval_timer.cancel()
            
            return user_input
        except Exception as e:
            return None
    
    def process_user_response(self, user_input: str) -> Dict[str, Any]:
        """Process user's response to approval request"""
        if not self.pending_approval:
            return {"error": "No pending approval"}
        
        user_input_lower = user_input.lower().strip()
        
        # Immediate approval
        if user_input_lower == "approve":
            self.is_approved = True
            self.pending_approval["status"] = "user_approved"
            return {
                "approved": True,
                "tables": self.pending_approval["selected_tables"],
                "method": "user_explicit"
            }
        
        # Rejection
        if user_input_lower == "reject":
            self.is_approved = True
            self.pending_approval["status"] = "rejected"
            return {
                "approved": False,
                "tables": [],
                "method": "user_rejected"
            }
        
        # Add tables
        if not user_input_lower.startswith("remove:"):
            # Treat as table names to add
            requested_tables = [t.strip() for t in user_input.split(",")]
            added_tables = []
            
            for table_name in requested_tables:
                if table_name and table_name != "approve":
                    # In real implementation, would fetch from schema
                    added_tables.append({
                        "table_name": table_name,
                        "relevance_score": "user_added",
                        "description": "User-requested table",
                        "columns": [],
                        "reasons": ["Added by user request"]
                    })
            
            if added_tables:
                self.pending_approval["selected_tables"].extend(added_tables)
                self.pending_approval["status"] = "modified"
                
                print(f"\n✅ Added tables: {[t['table_name'] for t in added_tables]}")
                print("Type 'approve' to confirm or wait for auto-approval...")
                
                # Restart timer
                self.approval_timer = threading.Timer(
                    self.auto_approve_timeout,
                    self._auto_approve
                )
                self.approval_timer.start()
                
                return {
                    "approved": False,
                    "tables": self.pending_approval["selected_tables"],
                    "method": "modified_pending",
                    "added": added_tables
                }
        
        # Remove tables
        if user_input_lower.startswith("remove:"):
            table_to_remove = user_input_lower.replace("remove:", "").strip()
            original_count = len(self.pending_approval["selected_tables"])
            
            self.pending_approval["selected_tables"] = [
                t for t in self.pending_approval["selected_tables"]
                if t["table_name"].lower() != table_to_remove
            ]
            
            if len(self.pending_approval["selected_tables"]) < original_count:
                print(f"\n❌ Removed table: {table_to_remove}")
                print("Type 'approve' to confirm or wait for auto-approval...")
                
                self.pending_approval["status"] = "modified"
                
                # Restart timer
                self.approval_timer = threading.Timer(
                    self.auto_approve_timeout,
                    self._auto_approve
                )
                self.approval_timer.start()
                
                return {
                    "approved": False,
                    "tables": self.pending_approval["selected_tables"],
                    "method": "modified_pending",
                    "removed": table_to_remove
                }
            else:
                return {
                    "approved": False,
                    "tables": self.pending_approval["selected_tables"],
                    "method": "not_found",
                    "message": f"Table '{table_to_remove}' not found in selection"
                }
        
        return {
            "approved": False,
            "tables": self.pending_approval["selected_tables"],
            "method": "unknown_command"
        }
    
    def wait_for_approval_interactive(self) -> Dict[str, Any]:
        """Interactive waiting for approval with user input"""
        while not self.is_approved:
            user_input = self.get_user_input()
            if user_input:
                result = self.process_user_response(user_input)
                if result.get("approved"):
                    return result
                elif result.get("error"):
                    print(f"Error: {result['error']}")
                    break
        
        # Return final state
        return {
            "approved": self.is_approved,
            "tables": self.pending_approval["selected_tables"] if self.pending_approval else [],
            "method": "auto" if self.pending_approval and self.pending_approval.get("status") == "auto_approved" else "user_explicit"
        }
    
    def get_final_tables(self) -> List[Dict[str, Any]]:
        """Get the final approved list of tables"""
        if self.pending_approval and self.is_approved:
            return self.pending_approval["selected_tables"]
        return []
    
    def cancel_approval(self):
        """Cancel the approval process"""
        if self.approval_timer:
            self.approval_timer.cancel()
        self.is_approved = True
        self.pending_approval = None


# Example usage
if __name__ == "__main__":
    agent = HITLValidatorAgent(auto_approve_timeout=5)
    
    # Mock selected tables
    mock_tables = [
        {
            "table_name": "hotel_bookings",
            "relevance_score": 4.5,
            "description": "Hotel reservation records",
            "columns": ["booking_id", "customer_id", "room_id", "check_in_date", "check_out_date", "total_amount", "booking_status"],
            "reasons": ["Matches business type: hotel", "Has date columns"]
        },
        {
            "table_name": "hotel_rooms",
            "relevance_score": 3.2,
            "description": "Individual hotel rooms",
            "columns": ["room_id", "hotel_id", "room_type_id", "room_number", "status"],
            "reasons": ["Related to hotel bookings"]
        },
        {
            "table_name": "customers",
            "relevance_score": 2.8,
            "description": "Customer information",
            "columns": ["customer_id", "first_name", "last_name", "email", "phone"],
            "reasons": ["Links to customers"]
        }
    ]
    
    query_context = {
        "original": "Show me hotel bookings for Q1",
        "structured": {
            "business_type": "hotel",
            "timeframe": {"label": "q1"}
        }
    }
    
    # Present for approval
    agent.present_tables_for_approval(mock_tables, query_context)
    
    # Wait for approval (interactive)
    result = agent.wait_for_approval_interactive()
    
    print("\n" + "="*60)
    print("FINAL RESULT:")
    print(f"Approved: {result['approved']}")
    print(f"Method: {result['method']}")
    print(f"Tables: {[t['table_name'] for t in result['tables']]}")
    print("="*60)
