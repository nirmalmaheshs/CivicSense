"""
Performance tab component for the evaluation dashboard.
Handles the display of TruLens metrics and trends.
"""

import streamlit as st
import pandas as pd
from typing import Dict
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_performance_gauge(value: float, title: str) -> go.Figure:
    """Create a gauge chart for metrics"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value * 100,  # Convert to percentage
        title={'text': title},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "rgb(50, 168, 82)"},
            'steps': [
                {'range': [0, 50], 'color': "rgb(255, 99, 132)"},
                {'range': [50, 75], 'color': "rgb(255, 205, 86)"},
                {'range': [75, 100], 'color': "rgb(75, 192, 192)"}
            ]
        }
    ))
    fig.update_layout(height=200)
    return fig

def create_metrics_timeline(metrics_df: pd.DataFrame) -> go.Figure:
    """Create timeline visualization of metrics"""
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=("Groundedness", "Context Relevance", "Answer Relevance")
    )

    metrics = ["Groundedness", "Context Relevance", "Answer Relevance"]
    colors = ["rgb(75, 192, 192)", "rgb(255, 159, 64)", "rgb(54, 162, 235)"]

    for idx, (metric, color) in enumerate(zip(metrics, colors), 1):
        fig.add_trace(
            go.Scatter(
                x=metrics_df['timestamp'],
                y=metrics_df[metric],
                name=metric,
                line=dict(color=color)
            ),
            row=idx, col=1
        )

    fig.update_layout(height=600, showlegend=False)
    return fig

def display_performance_metrics(metrics_df: pd.DataFrame):
    """
    Display the performance metrics section with TruLens evaluation results.

    Args:
        metrics_df: DataFrame containing TruLens metrics
    """
    if metrics_df.empty:
        st.info("No performance data available yet. Start chatting to generate TruLens metrics!")
        return

    st.subheader("🎯 RAG Performance Overview")

    # Calculate current metrics
    current_metrics = {
        "Groundedness": metrics_df["Groundedness"].mean(),
        "Context Relevance": metrics_df["Context Relevance"].mean(),
        "Answer Relevance": metrics_df["Answer Relevance"].mean()
    }

    # Display metric gauges
    cols = st.columns(3)
    for col, (metric, value) in zip(cols, current_metrics.items()):
        with col:
            fig = create_performance_gauge(value, metric)
            st.plotly_chart(fig, use_container_width=True)

    # Performance Timeline
    with st.expander("📈 Performance Timeline", expanded=True):
        st.plotly_chart(
            create_metrics_timeline(metrics_df),
            use_container_width=True
        )

    # Detailed Analysis
    with st.expander("📊 Detailed Analysis"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Recent Performance")
            recent_df = metrics_df.tail(5)
            st.dataframe(
                recent_df[["timestamp", "Groundedness", "Context Relevance", "Answer Relevance"]]
                .style.format({
                    "Groundedness": "{:.2%}",
                    "Context Relevance": "{:.2%}",
                    "Answer Relevance": "{:.2%}"
                })
            )

        with col2:
            st.markdown("### Statistics")
            stats = metrics_df[["Groundedness", "Context Relevance", "Answer Relevance"]].describe()
            st.dataframe(
                stats.style.format("{:.2%}")
            )

    # Query Analysis
    with st.expander("🔍 Query Analysis", expanded=True):
        if "query" in metrics_df.columns:
            st.markdown("### Sample Queries and Performance")

            # Get sample queries with their performance metrics
            sample_queries = metrics_df[["timestamp", "query", "Groundedness", "Context Relevance", "Answer Relevance"]].tail(10)

            for _, row in sample_queries.iterrows():
                with st.container():
                    st.markdown(f"**Query**: {row['query']}")
                    cols = st.columns(3)
                    for col, metric in zip(cols, ["Groundedness", "Context Relevance", "Answer Relevance"]):
                        with col:
                            st.metric(metric, f"{row[metric]:.1%}")
                    st.markdown("---")

def get_performance_summary(metrics_df: pd.DataFrame) -> Dict:
    """
    Generate a summary of TruLens performance metrics.

    Args:
        metrics_df: DataFrame containing TruLens metrics

    Returns:
        dict: Summary statistics for each metric
    """
    if metrics_df.empty:
        return {}

    metrics = ["Groundedness", "Context Relevance", "Answer Relevance"]
    summary = {}

    for metric in metrics:
        current = metrics_df[metric].mean()
        recent = metrics_df[metric].tail(5).mean()

        summary[metric.lower().replace(" ", "_")] = {
            "current": current,
            "recent": recent,
            "trend": recent - current,
            "min": metrics_df[metric].min(),
            "max": metrics_df[metric].max(),
            "std": metrics_df[metric].std()
        }

    return summary