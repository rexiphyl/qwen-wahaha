"""
LLMOps Dashboard - Visualizations for monitoring multi-agent system
"""
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any
from datetime import datetime

class LLMOpsDashboard:
    """Generate visualizations for LLMOps monitoring"""
    
    @staticmethod
    def create_confidence_chart(queries: List[Dict[str, Any]]) -> go.Figure:
        """Create confidence score distribution chart"""
        
        if not queries:
            return go.Figure().add_annotation(text="No data available", showarrow=False)
        
        confidences = [q.get("confidence", 0) for q in queries if q.get("confidence")]
        
        if not confidences:
            return go.Figure().add_annotation(text="No confidence data", showarrow=False)
        
        fig = go.Figure(data=[
            go.Histogram(
                x=confidences,
                nbinsx=20,
                marker_color='#3498db',
                opacity=0.75
            )
        ])
        
        fig.update_layout(
            title="Query Confidence Score Distribution",
            xaxis_title="Confidence Score",
            yaxis_title="Frequency",
            template="plotly_white",
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_success_rate_chart(queries: List[Dict[str, Any]]) -> go.Figure:
        """Create success rate pie chart"""
        
        if not queries:
            return go.Figure().add_annotation(text="No data available", showarrow=False)
        
        success_count = sum(1 for q in queries if q.get("success", False))
        fail_count = len(queries) - success_count
        
        fig = go.Figure(data=[
            go.Pie(
                labels=["Success", "Failed"],
                values=[success_count, fail_count],
                marker_colors=['#2ecc71', '#e74c3c'],
                hole=0.4
            )
        ])
        
        fig.update_layout(
            title="Query Success Rate",
            template="plotly_white",
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_agent_activity_chart(queries: List[Dict[str, Any]]) -> go.Figure:
        """Create agent activity heatmap"""
        
        if not queries:
            return go.Figure().add_annotation(text="No data available", showarrow=False)
        
        agent_counts = {}
        for query in queries:
            logs = query.get("agent_logs", [])
            for log in logs:
                agent = log.get("agent", "Unknown")
                action = log.get("action", "unknown")
                key = f"{agent}:{action}"
                agent_counts[key] = agent_counts.get(key, 0) + 1
        
        if not agent_counts:
            return go.Figure().add_annotation(text="No agent activity data", showarrow=False)
        
        agents = list(set(k.split(":")[0] for k in agent_counts.keys()))
        actions = list(set(k.split(":")[1] for k in agent_counts.keys()))
        
        # Create matrix
        z_data = []
        for agent in agents:
            row = []
            for action in actions:
                key = f"{agent}:{action}"
                row.append(agent_counts.get(key, 0))
            z_data.append(row)
        
        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=actions,
            y=agents,
            colorscale='Blues',
            showscale=True
        ))
        
        fig.update_layout(
            title="Agent Activity Heatmap",
            xaxis_title="Action",
            yaxis_title="Agent",
            template="plotly_white",
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_table_usage_chart(queries: List[Dict[str, Any]]) -> go.Figure:
        """Create table usage bar chart"""
        
        if not queries:
            return go.Figure().add_annotation(text="No data available", showarrow=False)
        
        table_counts = {}
        for query in queries:
            tables = query.get("relevant_tables", [])
            for table in tables:
                table_counts[table] = table_counts.get(table, 0) + 1
        
        if not table_counts:
            return go.Figure().add_annotation(text="No table usage data", showarrow=False)
        
        tables = list(table_counts.keys())
        counts = list(table_counts.values())
        
        fig = go.Figure(data=[
            go.Bar(
                x=tables,
                y=counts,
                marker_color='#9b59b6'
            )
        ])
        
        fig.update_layout(
            title="Database Table Usage Frequency",
            xaxis_title="Table Name",
            yaxis_title="Usage Count",
            template="plotly_white",
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_latency_chart(queries: List[Dict[str, Any]]) -> go.Figure:
        """Create query latency scatter plot (simulated based on agent count)"""
        
        if not queries:
            return go.Figure().add_annotation(text="No data available", showarrow=False)
        
        # Simulate latency based on agent count (since we don't track actual time yet)
        latencies = [q.get("metadata", {}).get("total_agents", 0) * 2.5 for q in queries]
        query_ids = list(range(1, len(queries) + 1))
        
        fig = go.Figure(data=[
            go.Scatter(
                x=query_ids,
                y=latencies,
                mode='lines+markers',
                line=dict(color='#e67e22', width=2),
                marker=dict(size=8)
            )
        ])
        
        fig.update_layout(
            title="Estimated Query Processing Time (by Agent Count)",
            xaxis_title="Query ID",
            yaxis_title="Estimated Time (seconds)",
            template="plotly_white",
            height=400
        )
        
        return fig
