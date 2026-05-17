"""Professional Streamlit UI for Text-to-SQL system with LLMOps dashboard."""
import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.config import Config
from src.agents.orchestrator import TextToSQLOrchestrator
from src.llmops.dashboard import LLMOpsDashboard


def initialize_session_state():
    """Initialize session state variables."""
    if "orchestrator" not in st.session_state:
        try:
            Config.validate()
            st.session_state.orchestrator = TextToSQLOrchestrator()
            st.session_state.metrics_history = []
        except ValueError as e:
            st.error(str(e))
            st.info("Please ensure OPENROUTER_API_KEY is set in your .env file")
            return False
    return True


def render_query_interface():
    """Render the main query interface."""
    st.title("🔍 Text-to-SQL Query System")
    st.markdown("Ask questions about your business data in natural language")
    
    # Example questions
    st.markdown("**Try these examples:**")
    example_cols = st.columns(3)
    examples = [
        "How many vegetarian orders were placed last week?",
        "Show me all hotel bookings this month",
        "What are the top 5 most expensive car rentals?"
    ]
    
    for i, example in enumerate(examples):
        if example_cols[i].button(example[:30] + "...", key=f"example_{i}"):
            st.session_state.query_input = example
    
    # Query input
    query = st.text_area(
        "Enter your question:",
        value=st.session_state.get("query_input", ""),
        height=100,
        placeholder="e.g., How many vegetarian orders were placed last week?",
        key="query_area"
    )
    
    if st.button("🚀 Run Query", type="primary", use_container_width=True):
        if query:
            with st.spinner("Processing your query..."):
                result = st.session_state.orchestrator.execute_query(query)
                
                # Store metrics
                st.session_state.metrics_history.append(result)
                
                # Display results
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader("📊 Results")
                    
                    if result["status"] == "success" and result["execution"]["data"]:
                        st.success(f"Query executed successfully! Found {result['execution']['row_count']} records")
                        
                        # Display SQL
                        with st.expander("📝 View Generated SQL", expanded=False):
                            st.code(result["sql"], language="sql")
                        
                        # Display data
                        st.dataframe(result["execution"]["data"], use_container_width=True)
                    elif result["status"] == "success":
                        st.info("Query executed but no results found")
                        with st.expander("📝 View Generated SQL"):
                            st.code(result["sql"], language="sql")
                    else:
                        st.error(f"Query failed: {result['execution'].get('error', 'Unknown error')}")
                        if result["sql"]:
                            with st.expander("📝 View Generated SQL"):
                                st.code(result["sql"], language="sql")
                
                with col2:
                    st.subheader("🎯 Intent Analysis")
                    st.metric("Confidence", f"{result['intent']['confidence']:.0%}")
                    st.markdown("**Detected Keywords:**")
                    st.write(", ".join(result["intent"]["keywords"]) if result["intent"]["keywords"] else "None")
                    st.markdown("**Target Tables:**")
                    st.write(", ".join(result["intent"]["tables"]))
                    
                    st.subheader("⚡ Performance")
                    st.metric("Total Latency", f"{result['total_latency_ms']}ms")
                    st.metric("Tokens Used", result["llm_metrics"]["total_tokens"])
        
        else:
            st.warning("Please enter a question")


def render_llmops_dashboard():
    """Render the LLMOps monitoring dashboard."""
    st.title("📈 LLMOps Dashboard")
    st.markdown("Monitor system performance and query analytics")
    
    if not st.session_state.get("metrics_history"):
        st.info("No queries have been run yet. Run some queries to see analytics.")
        return
    
    # Generate dashboard
    dashboard_data = LLMOpsDashboard.create_metrics_dashboard(st.session_state.metrics_history)
    
    if dashboard_data["figures"]:
        # Summary Statistics
        st.subheader("📊 Summary Statistics")
        summary = dashboard_data["figures"].get("summary", {})
        
        cols = st.columns(4)
        cols[0].metric("Total Queries", summary.get("total_queries", 0))
        cols[1].metric("Success Rate", f"{summary.get('success_rate', 0)}%")
        cols[2].metric("Avg Latency", f"{summary.get('avg_latency_ms', 0)}ms")
        cols[3].metric("Avg Tokens", summary.get("avg_tokens", 0))
        
        st.divider()
        
        # Charts
        chart_cols = st.columns(2)
        
        with chart_cols[0]:
            if "success_rate" in dashboard_data["figures"]:
                st.plotly_chart(dashboard_data["figures"]["success_rate"], use_container_width=True)
        
        with chart_cols[1]:
            if "confidence" in dashboard_data["figures"]:
                st.plotly_chart(dashboard_data["figures"]["confidence"], use_container_width=True)
        
        st.divider()
        
        latency_cols = st.columns(2)
        
        with latency_cols[0]:
            if "latency" in dashboard_data["figures"]:
                st.plotly_chart(dashboard_data["figures"]["latency"], use_container_width=True)
        
        with latency_cols[1]:
            if "tokens" in dashboard_data["figures"]:
                st.plotly_chart(dashboard_data["figures"]["tokens"], use_container_width=True)
        
        st.divider()
        
        # Recent Queries
        st.subheader("🕐 Recent Queries")
        if "recent_queries" in dashboard_data["figures"]:
            st.dataframe(dashboard_data["figures"]["recent_queries"], use_container_width=True)


def render_schema_info():
    """Render database schema information."""
    st.title("🗄️ Database Schema")
    st.markdown("Available tables and their descriptions")
    
    from src.core.schema import SCHEMA_METADATA
    
    for table_name, metadata in SCHEMA_METADATA.items():
        with st.expander(f"📋 {table_name.replace('_', ' ').title()}"):
            st.markdown(f"**Description:** {metadata['description']}")
            st.markdown("**Columns:**")
            st.write(", ".join(metadata["columns"]))


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Text-to-SQL Agent",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to:",
        ["Query Interface", "LLMOps Dashboard", "Database Schema"],
        index=0
    )
    
    st.sidebar.divider()
    
    # Sidebar info
    st.sidebar.markdown("### ⚙️ Configuration")
    st.sidebar.info(f"**Model:** {Config.MODEL_NAME}")
    st.sidebar.info(f"**Database:** {Config.DATABASE_PATH}")
    
    st.sidebar.divider()
    st.sidebar.markdown("### 🏷️ Powered by")
    st.sidebar.markdown("OpenRouter & NVIDIA Nemotron-3 Super")
    
    # Initialize session state
    if not initialize_session_state():
        return
    
    # Render selected page
    if page == "Query Interface":
        render_query_interface()
    elif page == "LLMOps Dashboard":
        render_llmops_dashboard()
    elif page == "Database Schema":
        render_schema_info()


if __name__ == "__main__":
    main()
