import streamlit as st
import os
import sys
import time
from datetime import datetime
import sqlite3

# Add project root directory to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from agents.business_agents.orchestrator import TextToSQLOrchestrator
from dotenv import load_dotenv

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Business Intelligence Agent",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for aesthetics
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .step-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #667eea;
    }
    
    .step-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .step-content {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 0.5rem;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
    }
    
    .thinking-box {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border: 2px dashed #667eea;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 1rem;
        color: #155724;
    }
    
    .error-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 8px;
        padding: 1rem;
        color: #721c24;
    }
    
    .table-badge {
        display: inline-block;
        background: #667eea;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 0.2rem;
    }
    
    .sql-code {
        background: #2d2d2d;
        color: #f8f8f2;
        padding: 1rem;
        border-radius: 8px;
        overflow-x: auto;
        font-family: 'Courier New', monospace;
    }
    
    .result-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
    }
    
    .result-table th {
        background: #667eea;
        color: white;
        padding: 0.8rem;
        text-align: left;
    }
    
    .result-table td {
        padding: 0.8rem;
        border-bottom: 1px solid #ddd;
    }
    
    .result-table tr:hover {
        background: #f5f5f5;
    }
    
    .sidebar-info {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .timer-bar {
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 2px;
        animation: countdown 5s linear;
    }
    
    @keyframes countdown {
        from { width: 100%; }
        to { width: 0%; }
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/hotel.png", width=80)
    st.title("🏨 BI Agent")
    
    st.markdown("""
    <div class='sidebar-info'>
        <strong>Business Domains:</strong><br>
        🏨 Hotels<br>
        🍽️ Restaurants<br>
        🚗 Car Rentals<br>
        💳 Payments & Reviews
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    if st.button("🗑️ Clear History", use_container_width=True):
        if 'history' in st.session_state:
            st.session_state.history = []
        st.rerun()
    
    st.markdown("---")
    st.caption("Powered by Groq & Llama 3.1")

# Main content
st.markdown('<h1 class="main-header">Business Intelligence Agent</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Ask questions about your hotel, restaurant, and car rental businesses</p>', unsafe_allow_html=True)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_query' not in st.session_state:
    st.session_state.current_query = ""
if 'pipeline_running' not in st.session_state:
    st.session_state.pipeline_running = False
if 'show_approval' not in st.session_state:
    st.session_state.show_approval = False
if 'selected_tables' not in st.session_state:
    st.session_state.selected_tables = []
if 'approval_timer' not in st.session_state:
    st.session_state.approval_timer = None

# Initialize orchestrator
@st.cache_resource
def get_orchestrator():
    return TextToSQLOrchestrator(interactive=False)

orchestrator = get_orchestrator()

# Display conversation history
if st.session_state.history:
    st.markdown("### 💬 Conversation History")
    for i, item in enumerate(st.session_state.history):
        with st.expander(f"Query {i+1}: {item['query']}", expanded=(i == len(st.session_state.history)-1)):
            if 'steps' in item:
                for step in item['steps']:
                    st.markdown(f"**{step['name']}**")
                    if step.get('content'):
                        st.markdown(step['content'])
                    if step.get('tables'):
                        tables_html = "".join([f'<span class="table-badge">{t}</span>' for t in step['tables']])
                        st.markdown(f"Tables: {tables_html}", unsafe_allow_html=True)
                    if step.get('sql'):
                        st.code(step['sql'], language='sql')
                    if step.get('result'):
                        st.dataframe(step['result'], use_container_width=True)
                    if step.get('response'):
                        st.success(step['response'])
                    st.divider()

st.divider()

# Query input
col1, col2 = st.columns([4, 1])
with col1:
    user_query = st.text_input(
        "💭 What would you like to know?",
        placeholder="e.g., How many hotel bookings do we have this month?",
        label_visibility="collapsed"
    )
with col2:
    submit_button = st.button("🚀 Ask", type="primary", use_container_width=True)

if submit_button and user_query:
    st.session_state.current_query = user_query
    st.session_state.pipeline_running = True
    st.session_state.show_approval = False
    st.rerun()

# Pipeline execution
if st.session_state.pipeline_running and st.session_state.current_query:
    query = st.session_state.current_query
    
    # Create a container for the pipeline steps
    pipeline_container = st.container()
    
    with pipeline_container:
        # Step 1: Query Rewriter
        with st.spinner("🤔 Agent is thinking about your question..."):
            time.sleep(0.5)  # Simulate thinking
            step1_placeholder = st.empty()
            
            # Call agent
            try:
                rewritten = orchestrator.rewrite_query(query, st.session_state.history)
                step1_content = f"""
                <div class='step-container'>
                    <div class='step-title'>📝 Step 1: Understanding Intent</div>
                    <div class='thinking-box'>
                        <strong>Original:</strong> {query}<br>
                        <strong>Rewritten:</strong> {rewritten.get('rewritten_query', query)}<br>
                        <strong>Business Type:</strong> {rewritten.get('business_type', 'unknown')}<br>
                        <strong>Aggregation:</strong> {rewritten.get('aggregation', 'none')}
                    </div>
                </div>
                """
                step1_placeholder.markdown(step1_content, unsafe_allow_html=True)
            except Exception as e:
                step1_placeholder.error(f"Error in Step 1: {str(e)}")
        
        # Step 2: Schema Retriever
        with st.spinner("🔍 Agent is finding relevant tables..."):
            time.sleep(0.5)
            step2_placeholder = st.empty()
            
            try:
                schema_result = orchestrator.retrieve_schema(rewritten.get('rewritten_query', query))
                tables = schema_result.get('tables', [])
                table_names = [t['table_name'] for t in tables]
                
                tables_html = "".join([f'<span class="table-badge">{t}</span>' for t in table_names])
                step2_content = f"""
                <div class='step-container'>
                    <div class='step-title'>🔍 Step 2: Finding Relevant Tables</div>
                    <div class='step-content'>
                        Found {len(tables)} relevant tables:<br><br>
                        {tables_html}
                    </div>
                </div>
                """
                step2_placeholder.markdown(step2_content, unsafe_allow_html=True)
                
                # Store for approval
                st.session_state.selected_tables = table_names
                st.session_state.show_approval = True
                
            except Exception as e:
                step2_placeholder.error(f"Error in Step 2: {str(e)}")
                st.session_state.pipeline_running = False
        
        # Step 3: Human-in-the-Loop Approval
        if st.session_state.show_approval:
            st.markdown("---")
            approval_col1, approval_col2 = st.columns([3, 1])
            
            with approval_col1:
                st.info(f"⏰ Auto-approval in 5 seconds unless you modify")
            
            with approval_col2:
                approve_btn = st.button("✅ Approve & Continue", type="primary", key="approve_btn")
            
            # Show timer
            timer_placeholder = st.empty()
            for i in range(5, 0, -1):
                timer_placeholder.markdown(f"""
                <div style='background: #fff3cd; padding: 1rem; border-radius: 8px; text-align: center;'>
                    ⏳ Auto-approving in <strong>{i}</strong> seconds...
                </div>
                """, unsafe_allow_html=True)
                time.sleep(1)
            
            timer_placeholder.empty()
            
            # Auto-approve if no interaction
            if approve_btn or True:  # Auto-approve after timer
                st.session_state.show_approval = False
                approved_tables = st.session_state.selected_tables
                
                # Step 4: SQL Generator
                with st.spinner("💻 Agent is writing SQL query..."):
                    time.sleep(0.5)
                    step4_placeholder = st.empty()
                    
                    try:
                        sql_result = orchestrator.generate_sql(query, approved_tables)
                        sql_query = sql_result.get('sql', '')
                        
                        step4_content = f"""
                        <div class='step-container'>
                            <div class='step-title'>💻 Step 4: Generating SQL</div>
                            <div class='step-content'>
                                <strong>Primary Table:</strong> {approved_tables[0] if approved_tables else 'N/A'}<br>
                                <strong>Tables Used:</strong> {', '.join(approved_tables)}
                            </div>
                            <div class='sql-code'>{sql_query}</div>
                        </div>
                        """
                        step4_placeholder.markdown(step4_content, unsafe_allow_html=True)
                        
                        # Step 5: Execute & Format
                        with st.spinner("📊 Agent is executing query and formatting results..."):
                            time.sleep(0.5)
                            step5_placeholder = st.empty()
                            
                            try:
                                result = orchestrator.execute_and_format(sql_query)
                                
                                if result.get('success'):
                                    step5_content = f"""
                                    <div class='step-container'>
                                        <div class='step-title'>📊 Step 5: Results</div>
                                        <div class='success-box'>
                                            <strong>{result.get('natural_language', 'Query executed successfully')}</strong>
                                        </div>
                                    </div>
                                    """
                                    step5_placeholder.markdown(step5_content, unsafe_allow_html=True)
                                    
                                    if result.get('data'):
                                        st.dataframe(result['data'], use_container_width=True)
                                    
                                    # Add to history
                                    st.session_state.history.append({
                                        'query': query,
                                        'steps': [
                                            {'name': 'Intent', 'content': rewritten.get('rewritten_query', query)},
                                            {'name': 'Tables', 'tables': approved_tables},
                                            {'name': 'SQL', 'sql': sql_query},
                                            {'name': 'Result', 'response': result.get('natural_language', '')}
                                        ]
                                    })
                                else:
                                    step5_placeholder.error(f"❌ Error: {result.get('error', 'Unknown error')}")
                                    
                            except Exception as e:
                                step5_placeholder.error(f"Error in Step 5: {str(e)}")
                                
                    except Exception as e:
                        step4_placeholder.error(f"Error in Step 4: {str(e)}")
                
                st.session_state.pipeline_running = False
                st.session_state.current_query = ""
                st.rerun()

# Footer
st.markdown("---")
st.caption("Built with Streamlit, Groq, and SQLite | Multi-turn context enabled")
