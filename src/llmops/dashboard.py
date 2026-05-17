"""LLMOps dashboard for monitoring text-to-SQL system performance."""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime


class LLMOpsDashboard:
    """Generate visualizations for LLMOps monitoring."""
    
    @staticmethod
    def create_metrics_dashboard(metrics_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create comprehensive LLMOps dashboard with multiple charts."""
        
        if not metrics_list:
            return {"message": "No metrics available", "figures": {}}
        
        # Convert to DataFrame for easier analysis
        df_data = []
        for m in metrics_list:
            row = {
                "timestamp": m.get("timestamp", ""),
                "status": m.get("status", "unknown"),
                "total_latency_ms": m.get("total_latency_ms", 0),
                "llm_latency_ms": m.get("llm_metrics", {}).get("latency_ms", 0),
                "input_tokens": m.get("llm_metrics", {}).get("input_tokens", 0),
                "output_tokens": m.get("llm_metrics", {}).get("output_tokens", 0),
                "total_tokens": m.get("llm_metrics", {}).get("total_tokens", 0),
                "confidence": m.get("intent", {}).get("confidence", 0),
                "question": m.get("question", "")[:50] + "..." if len(m.get("question", "")) > 50 else m.get("question", "")
            }
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        figures = {}
        
        # 1. Query Success Rate Over Time
        fig_success = go.Figure()
        success_counts = df.groupby(df["timestamp"].dt.minute).apply(
            lambda x: (x["status"] == "success").sum() / len(x) * 100 if len(x) > 0 else 0
        ).reset_index()
        success_counts.columns = ["minute", "success_rate"]
        
        fig_success.add_trace(go.Scatter(
            x=success_counts["minute"],
            y=success_counts["success_rate"],
            mode="lines+markers",
            name="Success Rate (%)",
            line=dict(color="green", width=2),
            marker=dict(size=8)
        ))
        
        fig_success.update_layout(
            title="Query Success Rate Over Time",
            xaxis_title="Time (minute)",
            yaxis_title="Success Rate (%)",
            yaxis_range=[0, 100],
            template="plotly_white",
            height=300
        )
        figures["success_rate"] = fig_success
        
        # 2. Latency Distribution
        fig_latency = make_subplots(rows=1, cols=2, subplot_titles=("Total Latency", "LLM Latency"))
        
        fig_latency.add_trace(go.Histogram(
            x=df["total_latency_ms"],
            name="Total Latency",
            marker_color="blue",
            opacity=0.7
        ), row=1, col=1)
        
        fig_latency.add_trace(go.Histogram(
            x=df["llm_latency_ms"],
            name="LLM Latency",
            marker_color="orange",
            opacity=0.7
        ), row=1, col=2)
        
        fig_latency.update_layout(
            title="Latency Distribution (ms)",
            showlegend=False,
            template="plotly_white",
            height=300
        )
        fig_latency.update_xaxes(title_text="Latency (ms)", row=1, col=1)
        fig_latency.update_xaxes(title_text="Latency (ms)", row=1, col=2)
        fig_latency.update_yaxes(title_text="Count", row=1, col=1)
        fig_latency.update_yaxes(title_text="Count", row=1, col=2)
        figures["latency"] = fig_latency
        
        # 3. Token Usage
        fig_tokens = go.Figure()
        fig_tokens.add_trace(go.Bar(
            x=list(range(len(df))),
            y=df["input_tokens"],
            name="Input Tokens",
            marker_color="steelblue"
        ))
        fig_tokens.add_trace(go.Bar(
            x=list(range(len(df))),
            y=df["output_tokens"],
            name="Output Tokens",
            marker_color="coral"
        ))
        
        fig_tokens.update_layout(
            title="Token Usage per Query",
            xaxis_title="Query Index",
            yaxis_title="Tokens",
            barmode="stack",
            template="plotly_white",
            height=300,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        figures["tokens"] = fig_tokens
        
        # 4. Confidence Score Distribution
        fig_confidence = go.Figure()
        fig_confidence.add_trace(go.Histogram(
            x=df["confidence"],
            name="Confidence Scores",
            marker_color="purple",
            nbinsx=20
        ))
        
        fig_confidence.update_layout(
            title="Intent Recognition Confidence Distribution",
            xaxis_title="Confidence Score",
            yaxis_title="Frequency",
            template="plotly_white",
            height=300
        )
        figures["confidence"] = fig_confidence
        
        # 5. Recent Queries Table
        recent_df = df.sort_values("timestamp", ascending=False).head(10)[
            ["timestamp", "status", "confidence", "total_latency_ms", "total_tokens", "question"]
        ].copy()
        recent_df["timestamp"] = recent_df["timestamp"].dt.strftime("%H:%M:%S")
        recent_df.columns = ["Time", "Status", "Confidence", "Latency (ms)", "Tokens", "Question"]
        
        figures["recent_queries"] = recent_df
        
        # 6. Summary Statistics
        summary_stats = {
            "total_queries": len(df),
            "successful": int((df["status"] == "success").sum()),
            "failed": int((df["status"] != "success").sum()),
            "success_rate": round((df["status"] == "success").mean() * 100, 2),
            "avg_latency_ms": round(df["total_latency_ms"].mean(), 2),
            "median_latency_ms": round(df["total_latency_ms"].median(), 2),
            "avg_tokens": round(df["total_tokens"].mean(), 2),
            "avg_confidence": round(df["confidence"].mean(), 3)
        }
        figures["summary"] = summary_stats
        
        return {"message": "Dashboard generated successfully", "figures": figures}
