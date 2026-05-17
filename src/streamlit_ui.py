"""
Streamlit UI - Main application interface for Multi-Agent Text-to-SQL System
Features: Query interface, Results display, LLMOps Dashboard
"""
import streamlit as st
import pandas as pd
from src.core.config import Config
from src.agents.orchestrator import OrchestratorAgent
from src.llmops.dashboard import LLMOpsDashboard

# Page configuration
st.set_page_config(
    page_title="Multi-Agent Text-to-SQL",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for query history
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "current_result" not in st.session_state:
    st.session_state.current_result = None

# Custom CSS
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; color: #2c3e50; text-align: center;}
    .agent-log {background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin: 5px 0;}
    .success-box {background-color: #d4edda; padding: 15px; border-radius: 5px; border-left: 4px solid #28a745;}
    .error-box {background-color: #f8d7da; padding: 15px; border-radius: 5px; border-left: 4px solid #dc3545;}
    .info-box {background-color: #d1ecf1; padding: 15px; border-radius: 5px; border-left: 4px solid #17a2b8;}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='main-header'>🤖 Multi-Agent Text-to-SQL System</h1>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    st.info(f"**Model:** {Config.MODEL_NAME}")
    st.info(f"**Database:** {Config.DATABASE_PATH}")
    
    st.markdown("---")
    st.subheader("📊 Quick Stats")
    total_queries = len(st.session_state.query_history)
    successful_queries = sum(1 for q in st.session_state.query_history if q.get("success"))
    st.metric("Total Queries", total_queries)
    st.metric("Success Rate", f"{(successful_queries/total_queries*100):.1f}%" if total_queries > 0 else "N/A")
    
    st.markdown("---")
    st.subheader("🗂️ Available Tables")
    try:
        import sqlite3
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        for table in tables:
            st.caption(f"• {table}")
    except Exception as e:
        st.error(f"Could not load tables: {e}")

# Main content area with tabs
tab1, tab2 = st.tabs(["🔍 Query Interface", "📈 LLMOps Dashboard"])

# Tab 1: Query Interface
with tab1:
    st.header("Ask Your Question")
    
    # Query input
    user_query = st.text_area(
        "Enter your question:",
        placeholder="e.g., How many vegetarian orders were placed last week?",
        height=100
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        submit_btn = st.button("🚀 Run Query", type="primary", use_container_width=True)
    
    # Process query
    if submit_btn and user_query:
        with st.spinner("🤖 Agents are processing your query..."):
            try:
                orchestrator = OrchestratorAgent()
                result = orchestrator.process_query(user_query)
                st.session_state.current_result = result
                st.session_state.query_history.append(result)
                
                # Display results
                if result["success"]:
                    st.success("✅ Query executed successfully!")
                    
                    # Show agent workflow
                    with st.expander("🔍 Agent Workflow", expanded=True):
                        st.markdown("**Intent Recognition:**")
                        st.info(f"Identified Intent: {result['intent']}")
                        st.write(f"**Relevant Tables:** {', '.join(result['relevant_tables'])}")
                        st.write(f"**Confidence Score:** {result['confidence']:.2f}")
                        
                        st.markdown("**SQL Generation:**")
                        st.code(result['sql'], language='sql')
                        
                        st.markdown("**Agent Logs:**")
                        for log in result['agent_logs']:
                            st.markdown(f"<div class='agent-log'><strong>{log['agent']}</strong>: {log['action']}<br><small>{log['details']}</small></div>", unsafe_allow_html=True)
                    
                    # Show results
                    if result["result"]:
                        st.markdown("**Results:**")
                        df = pd.DataFrame(
                            result["result"]["rows"],
                            columns=result["result"]["columns"]
                        )
                        st.dataframe(df, use_container_width=True)
                        st.caption(f"Total rows: {result['result']['count']}")
                else:
                    st.error(f"❌ {result['error']}")
                    if result['agent_logs']:
                        with st.expander("View Agent Logs"):
                            for log in result['agent_logs']:
                                st.markdown(f"<div class='agent-log'><strong>{log['agent']}</strong>: {log['action']}<br><small>{log['details']}</small></div>", unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"System error: {str(e)}")
                st.exception(e)
    
    elif submit_btn and not user_query:
        st.warning("Please enter a question first.")
    
    # Show current result if exists
    if st.session_state.current_result and not submit_btn:
        st.markdown("---")
        st.subheader("Previous Result")
        result = st.session_state.current_result
        if result["success"]:
            st.success("✅ Query executed successfully!")
            st.code(result['sql'], language='sql')
            if result["result"]:
                df = pd.DataFrame(
                    result["result"]["rows"],
                    columns=result["result"]["columns"]
                )
                st.dataframe(df, use_container_width=True)

# Tab 2: LLMOps Dashboard
with tab2:
    st.header("📈 LLMOps Dashboard")
    
    if len(st.session_state.query_history) == 0:
        st.info("No queries yet. Run some queries to see analytics!")
    else:
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        total = len(st.session_state.query_history)
        successful = sum(1 for q in st.session_state.query_history if q.get("success"))
        avg_confidence = sum(q.get("confidence", 0) for q in st.session_state.query_history) / total if total > 0 else 0
        
        col1.metric("Total Queries", total)
        col2.metric("Successful", successful, delta=f"{(successful/total*100):.1f}%" if total > 0 else None)
        col3.metric("Failed", total - successful)
        col4.metric("Avg Confidence", f"{avg_confidence:.2f}")
        
        st.markdown("---")
        
        # Charts row 1
        col1, col2 = st.columns(2)
        with col1:
            fig = LLMOpsDashboard.create_success_rate_chart(st.session_state.query_history)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = LLMOpsDashboard.create_confidence_chart(st.session_state.query_history)
            st.plotly_chart(fig, use_container_width=True)
        
        # Charts row 2
        col1, col2 = st.columns(2)
        with col1:
            fig = LLMOpsDashboard.create_table_usage_chart(st.session_state.query_history)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = LLMOpsDashboard.create_agent_activity_chart(st.session_state.query_history)
            st.plotly_chart(fig, use_container_width=True)
        
        # Latency chart
        fig = LLMOpsDashboard.create_latency_chart(st.session_state.query_history)
        st.plotly_chart(fig, use_container_width=True)
        
        # Recent queries table
        st.markdown("---")
        st.subheader("Recent Queries Log")
        
        log_data = []
        for i, query in enumerate(reversed(st.session_state.query_history[-10:])):
            log_data.append({
                "#": len(st.session_state.query_history) - i,
                "Query": query.get("query", "")[:50] + "..." if len(query.get("query", "")) > 50 else query.get("query", ""),
                "Intent": query.get("intent", "N/A"),
                "Tables": ", ".join(query.get("relevant_tables", [])),
                "Success": "✅" if query.get("success") else "❌",
                "Confidence": f"{query.get('confidence', 0):.2f}"
            })
        
        st.dataframe(pd.DataFrame(log_data), use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d;'>
    <p>Built with 🤖 Multi-Agent Architecture | Powered by OpenRouter & NVIDIA Nemotron-3 Super</p>
</div>
""", unsafe_allow_html=True)
