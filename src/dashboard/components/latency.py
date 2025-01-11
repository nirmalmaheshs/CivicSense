"""
Latency analysis component for the evaluation dashboard.
Handles RAG pipeline timing analysis using TruLens records.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict

def create_latency_timeline(df: pd.DataFrame) -> go.Figure:
    """Create timeline visualization of latency metrics"""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Total Latency", "Component Breakdown"),
        specs=[[{"type": "scatter"}], [{"type": "bar"}]]
    )

    # Add total latency line
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['total_latency_ms'],
            name="Total Latency",
            line=dict(color="rgb(75, 192, 192)")
        ),
        row=1, col=1
    )

    # Add component breakdown
    components = ['retrieval_time_ms', 'generation_time_ms']
    colors = ["rgb(255, 159, 64)", "rgb(54, 162, 235)"]

    for component, color in zip(components, colors):
        if component in df.columns:
            fig.add_trace(
                go.Bar(
                    x=df['timestamp'],
                    y=df[component],
                    name=component.replace('_time_ms', '').title(),
                    marker_color=color
                ),
                row=2, col=1
            )

    fig.update_layout(
        height=600,
        showlegend=True,
        barmode='stack'
    )

    return fig

def display_latency_metrics(latency_df: pd.DataFrame):
    """
    Display latency metrics from TruLens records.

    Args:
        latency_df: DataFrame containing latency data
    """
    if latency_df.empty:
        st.info("No latency data available yet. Start chatting to generate timing data!")
        return

    st.subheader("⚡ Latency Analysis")

    # Calculate overall metrics
    avg_total = latency_df['total_latency_ms'].mean()
    p95_total = latency_df['total_latency_ms'].quantile(0.95)
    avg_retrieval = latency_df['retrieval_time_ms'].mean() if 'retrieval_time_ms' in latency_df.columns else 0
    avg_generation = latency_df['generation_time_ms'].mean() if 'generation_time_ms' in latency_df.columns else 0

    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Avg Total Latency",
            f"{avg_total:.0f}ms",
            help="Average total response time"
        )

    with col2:
        st.metric(
            "95th Percentile",
            f"{p95_total:.0f}ms",
            help="95% of requests are faster than this"
        )

    with col3:
        st.metric(
            "Avg Retrieval Time",
            f"{avg_retrieval:.0f}ms",
            help="Average time for context retrieval"
        )

    with col4:
        st.metric(
            "Avg Generation Time",
            f"{avg_generation:.0f}ms",
            help="Average time for response generation"
        )

    # Latency Timeline
    with st.expander("📈 Latency Timeline", expanded=True):
        fig = create_latency_timeline(latency_df)
        st.plotly_chart(fig, use_container_width=True)

    # Detailed Analysis
    with st.expander("📊 Detailed Analysis"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Component Distribution")
            if all(col in latency_df.columns for col in ['retrieval_time_ms', 'generation_time_ms']):
                component_dist = pd.DataFrame({
                    'Component': ['Retrieval', 'Generation'],
                    'Average Time (ms)': [avg_retrieval, avg_generation],
                    'Percentage': [
                        avg_retrieval / avg_total * 100 if avg_total > 0 else 0,
                        avg_generation / avg_total * 100 if avg_total > 0 else 0
                    ]
                })

                st.dataframe(
                    component_dist.style.format({
                        'Average Time (ms)': '{:.0f}',
                        'Percentage': '{:.1f}%'
                    })
                )

        with col2:
            st.markdown("### Statistics")
            stats_df = latency_df[['total_latency_ms']].describe()
            st.dataframe(
                stats_df.style.format('{:.1f}')
            )

    # Performance Thresholds
    with st.expander("🎯 Performance Thresholds"):
        thresholds = {
            'Excellent': 1000,  # 1 second
            'Good': 2000,      # 2 seconds
            'Fair': 3000,      # 3 seconds
            'Poor': float('inf')
        }

        performance_dist = {}
        total_requests = len(latency_df)

        prev_threshold = 0
        for category, threshold in thresholds.items():
            count = len(latency_df[
                (latency_df['total_latency_ms'] > prev_threshold) &
                (latency_df['total_latency_ms'] <= threshold)
            ])
            performance_dist[category] = (count / total_requests * 100) if total_requests > 0 else 0
            prev_threshold = threshold

        st.markdown("### Response Time Distribution")
        perf_df = pd.DataFrame({
            'Category': performance_dist.keys(),
            'Percentage': performance_dist.values()
        })

        st.dataframe(
            perf_df.style.format({
                'Percentage': '{:.1f}%'
            })
        )

def get_latency_summary(latency_df: pd.DataFrame) -> Dict:
    """
    Generate summary of latency metrics.

    Args:
        latency_df: DataFrame containing latency data

    Returns:
        dict: Summary statistics for latency
    """
    if latency_df.empty:
        return {}

    total_latency = latency_df['total_latency_ms']
    components = {
        'retrieval': 'retrieval_time_ms',
        'generation': 'generation_time_ms'
    }

    summary = {
        'total': {
            'average': total_latency.mean(),
            'p95': total_latency.quantile(0.95),
            'min': total_latency.min(),
            'max': total_latency.max(),
            'std': total_latency.std()
        }
    }

    for component, column in components.items():
        if column in latency_df.columns:
            component_data = latency_df[column]
            summary[component] = {
                'average': component_data.mean(),
                'p95': component_data.quantile(0.95),
                'percentage': (component_data.sum() / total_latency.sum() * 100)
                            if total_latency.sum() > 0 else 0
            }

    return summary