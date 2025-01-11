"""
Token usage component for the evaluation dashboard.
Handles the display of token usage metrics and trends.
"""

import streamlit as st
import pandas as pd
from typing import Dict
from ..visualizations import create_token_usage_trend


def display_token_metrics(token_df: pd.DataFrame):
    """
    Display the token usage metrics section.

    Args:
        token_df: DataFrame containing token usage data
    """
    if token_df.empty:
        st.info("No token usage data available yet. Start chatting to generate data!")
        return

    # Summary metrics
    st.subheader("🔤 Token Usage Summary")

    total_tokens = token_df['total_tokens'].sum()
    total_cost = (token_df['prompt_tokens'].sum() * 0.7 +
                  token_df['completion_tokens'].sum() * 2.0) / 1000  # Cost per 1K tokens

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Tokens",
            f"{total_tokens:,}",
            help="Total number of tokens used (prompts + completions)"
        )

    with col2:
        avg_per_query = token_df['total_tokens'].mean()
        st.metric(
            "Avg Tokens/Query",
            f"{avg_per_query:.0f}",
            help="Average number of tokens used per query"
        )

    with col3:
        completion_ratio = (token_df['completion_tokens'].sum() /
                            total_tokens * 100)
        st.metric(
            "Completion Ratio",
            f"{completion_ratio:.1f}%",
            help="Percentage of tokens used for completions"
        )

    with col4:
        st.metric(
            "Estimated Cost",
            f"${total_cost:.2f}",
            help="Estimated cost based on current token pricing"
        )

    # Usage Trends
    with st.expander("📈 Usage Trends", expanded=True):
        st.markdown("### Token Usage Over Time")
        trend_fig = create_token_usage_trend(token_df)
        st.plotly_chart(trend_fig, use_container_width=True)

    # Daily Statistics
    with st.expander("📊 Daily Statistics"):
        daily_stats = get_daily_token_stats(token_df)

        st.markdown("### Daily Token Usage")
        st.dataframe(
            daily_stats.style.format({
                'Total Tokens': '{:,.0f}',
                'Prompt Tokens': '{:,.0f}',
                'Completion Tokens': '{:,.0f}',
                'Queries': '{:,.0f}',
                'Avg Tokens/Query': '{:.1f}',
                'Estimated Cost': '${:.2f}'
            })
        )


def get_daily_token_stats(token_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate daily token usage statistics.

    Args:
        token_df: DataFrame containing token usage data

    Returns:
        DataFrame: Daily token usage statistics
    """
    daily_stats = (token_df
                   .set_index('timestamp')
                   .resample('D')
                   .agg({
        'total_tokens': 'sum',
        'prompt_tokens': 'sum',
        'completion_tokens': 'sum'
    })
                   .reset_index()
                   )

    # Calculate additional metrics
    daily_stats['Queries'] = (token_df
                              .set_index('timestamp')
                              .resample('D')
                              .size()
                              .values
                              )

    daily_stats = daily_stats.rename(columns={
        'total_tokens': 'Total Tokens',
        'prompt_tokens': 'Prompt Tokens',
        'completion_tokens': 'Completion Tokens'
    })

    daily_stats['Avg Tokens/Query'] = (
            daily_stats['Total Tokens'] / daily_stats['Queries']
    )

    daily_stats['Estimated Cost'] = (
            (daily_stats['Prompt Tokens'] * 0.7 +
             daily_stats['Completion Tokens'] * 2.0) / 1000
    )

    return daily_stats.sort_values('timestamp', ascending=False)


def get_token_usage_summary(token_df: pd.DataFrame) -> Dict:
    """
    Generate a summary of token usage metrics.

    Args:
        token_df: DataFrame containing token usage data

    Returns:
        dict: Summary statistics for token usage
    """
    if token_df.empty:
        return {}

    total_tokens = token_df['total_tokens'].sum()
    prompt_tokens = token_df['prompt_tokens'].sum()
    completion_tokens = token_df['completion_tokens'].sum()

    return {
        'total_tokens': total_tokens,
        'prompt_tokens': prompt_tokens,
        'completion_tokens': completion_tokens,
        'avg_per_query': token_df['total_tokens'].mean(),
        'completion_ratio': completion_tokens / total_tokens if total_tokens > 0 else 0,
        'estimated_cost': (prompt_tokens * 0.7 + completion_tokens * 2.0) / 1000
    }