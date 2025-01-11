"""
Cost analysis component for the evaluation dashboard.
Handles the display of cost metrics, trends, and analysis.
"""

import streamlit as st
import pandas as pd
from typing import Dict
from datetime import datetime, timedelta
from ..visualizations import create_cost_analysis


def display_cost_metrics(cost_df: pd.DataFrame):
    """
    Display the cost metrics section.

    Args:
        cost_df: DataFrame containing cost data
    """
    if cost_df.empty:
        st.info("No cost data available yet. Start chatting to generate data!")
        return

    # Summary metrics
    st.subheader("💰 Cost Summary")

    # Calculate periods
    now = pd.Timestamp.now()
    last_24h = cost_df[cost_df['timestamp'] > now - pd.Timedelta(hours=24)]
    last_7d = cost_df[cost_df['timestamp'] > now - pd.Timedelta(days=7)]
    last_30d = cost_df[cost_df['timestamp'] > now - pd.Timedelta(days=30)]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_cost = cost_df['cost'].sum()
        st.metric(
            "Total Cost",
            f"${total_cost:.2f}",
            help="Total cost across all interactions"
        )

    with col2:
        daily_avg = last_30d['cost'].sum() / 30 if not last_30d.empty else 0
        st.metric(
            "Daily Average",
            f"${daily_avg:.2f}",
            help="Average daily cost (last 30 days)"
        )

    with col3:
        last_24h_cost = last_24h['cost'].sum()
        delta = last_24h_cost - daily_avg
        st.metric(
            "Last 24 Hours",
            f"${last_24h_cost:.2f}",
            f"{delta:+.2f}",
            help="Cost in the last 24 hours vs daily average"
        )

    with col4:
        avg_cost_per_query = cost_df['cost'].mean()
        st.metric(
            "Avg Cost/Query",
            f"${avg_cost_per_query:.4f}",
            help="Average cost per interaction"
        )

    # Cost Trends
    with st.expander("📈 Cost Trends", expanded=True):
        st.markdown("### Cost Over Time")
        trend_fig = create_cost_analysis(cost_df)
        st.plotly_chart(trend_fig, use_container_width=True)

    # Period Analysis
    with st.expander("📅 Period Analysis"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Recent Periods")
            periods = {
                "Last 24 Hours": last_24h['cost'].sum(),
                "Last 7 Days": last_7d['cost'].sum(),
                "Last 30 Days": last_30d['cost'].sum(),
                "All Time": total_cost
            }

            for period, cost in periods.items():
                st.metric(period, f"${cost:.2f}")

        with col2:
            st.markdown("### Daily Averages")
            averages = {
                "This Week": last_7d['cost'].sum() / 7 if not last_7d.empty else 0,
                "This Month": last_30d['cost'].sum() / 30 if not last_30d.empty else 0,
                "All Time": total_cost / (
                        (cost_df['timestamp'].max() - cost_df['timestamp'].min()).days + 1
                ) if not cost_df.empty else 0
            }

            for period, avg in averages.items():
                st.metric(f"{period} (Daily Avg)", f"${avg:.2f}")

    # Cost Breakdown
    with st.expander("🔍 Cost Breakdown"):
        st.markdown("### Daily Cost Breakdown")
        daily_costs = analyze_daily_costs(cost_df)

        st.dataframe(
            daily_costs.style.format({
                'Total Cost': '${:.2f}',
                'Queries': '{:.0f}',
                'Avg Cost/Query': '${:.4f}',
                'Cumulative Cost': '${:.2f}'
            })
        )


def analyze_daily_costs(cost_df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze costs aggregated by day.

    Args:
        cost_df: DataFrame containing cost data

    Returns:
        DataFrame: Daily cost analysis
    """
    if cost_df.empty:
        return pd.DataFrame()

    daily_costs = (cost_df
                   .set_index('timestamp')
                   .resample('D')
                   .agg({
        'cost': ['sum', 'count']
    })
                   .reset_index())

    daily_costs.columns = ['Date', 'Total Cost', 'Queries']
    daily_costs['Avg Cost/Query'] = daily_costs['Total Cost'] / daily_costs['Queries']
    daily_costs['Cumulative Cost'] = daily_costs['Total Cost'].cumsum()

    return daily_costs.sort_values('Date', ascending=False)


def get_cost_summary(cost_df: pd.DataFrame) -> Dict:
    """
    Generate a summary of cost metrics.

    Args:
        cost_df: DataFrame containing cost data

    Returns:
        dict: Summary statistics for costs
    """
    if cost_df.empty:
        return {}

    now = pd.Timestamp.now()
    last_24h = cost_df[cost_df['timestamp'] > now - pd.Timedelta(hours=24)]
    last_7d = cost_df[cost_df['timestamp'] > now - pd.Timedelta(days=7)]
    last_30d = cost_df[cost_df['timestamp'] > now - pd.Timedelta(days=30)]

    return {
        'total_cost': cost_df['cost'].sum(),
        'avg_cost_per_query': cost_df['cost'].mean(),
        'last_24h_cost': last_24h['cost'].sum(),
        'last_7d_cost': last_7d['cost'].sum(),
        'last_30d_cost': last_30d['cost'].sum(),
        'daily_average': last_30d['cost'].sum() / 30 if not last_30d.empty else 0,
        'total_queries': len(cost_df),
        'cost_trend': (last_24h['cost'].sum() /
                       (last_7d['cost'].sum() / 7) if not last_7d.empty else 0)
    }