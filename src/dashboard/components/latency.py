"""
Latency analysis component for the evaluation dashboard.
Handles the display of response time metrics and trends.
"""

import streamlit as st
import pandas as pd
from typing import Dict
from ..visualizations import create_latency_trend


def display_latency_metrics(latency_df: pd.DataFrame):
    """
    Display the latency metrics section.

    Args:
        latency_df: DataFrame containing latency data
    """
    if latency_df.empty:
        st.info("No latency data available yet. Start chatting to generate data!")
        return

    # Summary metrics
    st.subheader("⚡ Latency Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        avg_latency = latency_df['latency_ms'].mean()
        st.metric(
            "Average Latency",
            f"{avg_latency:.0f}ms",
            help="Average response time in milliseconds"
        )

    with col2:
        p95_latency = latency_df['latency_ms'].quantile(0.95)
        st.metric(
            "95th Percentile",
            f"{p95_latency:.0f}ms",
            help="95% of requests are faster than this"
        )

    with col3:
        max_latency = latency_df['latency_ms'].max()
        st.metric(
            "Max Latency",
            f"{max_latency:.0f}ms",
            help="Maximum response time observed"
        )

    with col4:
        recent_avg = latency_df['latency_ms'].tail(10).mean()
        delta = recent_avg - avg_latency
        st.metric(
            "Recent Average",
            f"{recent_avg:.0f}ms",
            f"{delta:+.0f}ms",
            help="Average of last 10 requests vs overall average"
        )

    # Response Time Trends
    with st.expander("📈 Response Time Trends", expanded=True):
        st.markdown("### Latency Over Time")
        trend_fig = create_latency_trend(latency_df)
        st.plotly_chart(trend_fig, use_container_width=True)

    # Detailed Statistics
    with st.expander("📊 Detailed Statistics"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Distribution Statistics")
            stats = latency_df['latency_ms'].describe()
            metrics = {
                "Count": f"{stats['count']:.0f}",
                "Mean": f"{stats['mean']:.0f}ms",
                "Std Dev": f"{stats['std']:.0f}ms",
                "Min": f"{stats['min']:.0f}ms",
                "25%": f"{stats['25%']:.0f}ms",
                "Median": f"{stats['50%']:.0f}ms",
                "75%": f"{stats['75%']:.0f}ms",
                "Max": f"{stats['max']:.0f}ms"
            }

            for name, value in metrics.items():
                st.metric(name, value)

        with col2:
            st.markdown("### Percentile Analysis")
            percentiles = [50, 75, 90, 95, 99, 99.9]
            for p in percentiles:
                value = latency_df['latency_ms'].quantile(p / 100)
                st.metric(f"P{p}", f"{value:.0f}ms")

    # Time-based Analysis
    with st.expander("🕒 Time-based Analysis"):
        latency_df['hour'] = latency_df['timestamp'].dt.hour
        hourly_stats = (latency_df.groupby('hour')['latency_ms']
                        .agg(['mean', 'count', 'std'])
                        .round(2))

        st.markdown("### Hourly Performance")
        st.dataframe(
            hourly_stats.style.format({
                'mean': '{:.0f}ms',
                'count': '{:.0f}',
                'std': '{:.0f}ms'
            })
        )


def get_latency_summary(latency_df: pd.DataFrame) -> Dict:
    """
    Generate a summary of latency metrics.

    Args:
        latency_df: DataFrame containing latency data

    Returns:
        dict: Summary statistics for latency
    """
    if latency_df.empty:
        return {}

    return {
        'average': latency_df['latency_ms'].mean(),
        'p95': latency_df['latency_ms'].quantile(0.95),
        'max': latency_df['latency_ms'].max(),
        'recent_avg': latency_df['latency_ms'].tail(10).mean(),
        'std_dev': latency_df['latency_ms'].std(),
        'total_requests': len(latency_df),
        'percentiles': {
            p: latency_df['latency_ms'].quantile(p / 100)
            for p in [50, 75, 90, 95, 99, 99.9]
        }
    }


def analyze_latency_thresholds(latency_df: pd.DataFrame,
                               thresholds: Dict[str, float]) -> Dict[str, float]:
    """
    Analyze what percentage of requests fall within given thresholds.

    Args:
        latency_df: DataFrame containing latency data
        thresholds: Dictionary of threshold names and their values in ms

    Returns:
        dict: Percentage of requests within each threshold
    """
    if latency_df.empty:
        return {name: 0.0 for name in thresholds}

    results = {}
    total_requests = len(latency_df)

    for name, threshold in thresholds.items():
        count = (latency_df['latency_ms'] <= threshold).sum()
        results[name] = (count / total_requests) * 100

    return results