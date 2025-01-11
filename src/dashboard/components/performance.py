"""
Performance tab component for the evaluation dashboard.
Handles the display of performance metrics and trends.
"""

import streamlit as st
import pandas as pd
from typing import List

from ..visualizations import (
    create_performance_trend,
    create_score_distribution
)


def display_performance_metrics(metrics_df: pd.DataFrame):
    """
    Display the performance metrics section.

    Args:
        metrics_df: DataFrame containing performance metrics
    """
    if metrics_df.empty:
        st.info("No performance metrics available yet. Start chatting to generate data!")
        return

    metrics = ['context_relevance', 'response_relevance', 'completion_quality']

    # Summary metrics
    st.subheader("📊 Overall Performance")
    cols = st.columns(3)
    for col, metric in zip(cols, metrics):
        with col:
            avg_val = metrics_df[metric].mean()
            recent_val = metrics_df[metric].iloc[-5:].mean() if len(metrics_df) >= 5 else avg_val
            delta = recent_val - avg_val

            st.metric(
                label=metric.replace('_', ' ').title(),
                value=f"{recent_val:.2f}",
                delta=f"{delta:+.2f} from average",
                help=f"Recent average vs overall average ({avg_val:.2f})"
            )

    # Detailed Analysis Section
    with st.expander("📈 Detailed Analysis", expanded=True):
        # Performance Trend
        st.markdown("### Performance Over Time")
        trend_fig = create_performance_trend(metrics_df, metrics)
        st.plotly_chart(trend_fig, use_container_width=True)

        # Distribution Analysis
        st.markdown("### Score Distribution")
        dist_fig = create_score_distribution(metrics_df, metrics)
        st.plotly_chart(dist_fig, use_container_width=True)

    # Statistical Summary
    with st.expander("📊 Statistical Summary"):
        for metric in metrics:
            st.markdown(f"**{metric.replace('_', ' ').title()}**")
            stats = metrics_df[metric].describe()

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Mean", f"{stats['mean']:.2f}")
                st.metric("Std Dev", f"{stats['std']:.2f}")
            with col2:
                st.metric("Median", f"{stats['50%']:.2f}")
                st.metric("Count", f"{stats['count']:.0f}")
            with col3:
                st.metric("Min", f"{stats['min']:.2f}")
                st.metric("Max", f"{stats['max']:.2f}")

    # Recent Performance Analysis
    # Recent Performance Analysis
    with st.expander("🎯 Recent Performance", expanded=True):
        recent_data = metrics_df.iloc[-10:] if len(metrics_df) > 10 else metrics_df

        st.markdown("### Last 10 Interactions")

        # First show the metrics table
        st.markdown("#### Performance Metrics")
        metrics_view = recent_data[['timestamp'] + metrics].copy()
        st.dataframe(
            metrics_view
            .style.format({
                'timestamp': lambda x: x.strftime('%Y-%m-%d %H:%M:%S'),
                'context_relevance': '{:.2f}',
                'response_relevance': '{:.2f}',
                'completion_quality': '{:.2f}'
            })
            .background_gradient(subset=metrics, cmap='RdYlGn')
        )

        # Then show the Q&A details
        st.markdown("#### Questions and Answers")
        for _, row in recent_data.iloc[::-1].iterrows():  # Reverse order to show most recent first
            with st.container():
                st.markdown(f"**Time**: {row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Question**")
                    st.info(row.get('question', 'N/A'))
                with col2:
                    st.markdown("**Answer**")
                    st.success(row.get('answer', 'N/A'))
                st.divider()


def get_performance_summary(metrics_df: pd.DataFrame) -> dict:
    """
    Generate a summary of performance metrics.

    Args:
        metrics_df: DataFrame containing performance metrics

    Returns:
        dict: Summary statistics for each metric
    """
    if metrics_df.empty:
        return {}

    metrics = ['context_relevance', 'response_relevance', 'completion_quality']
    summary = {}

    for metric in metrics:
        recent = metrics_df[metric].iloc[-5:].mean() if len(metrics_df) >= 5 else metrics_df[metric].mean()
        overall = metrics_df[metric].mean()

        summary[metric] = {
            'recent': recent,
            'overall': overall,
            'trend': recent - overall,
            'min': metrics_df[metric].min(),
            'max': metrics_df[metric].max()
        }

    return summary