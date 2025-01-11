"""
Token usage component for the evaluation dashboard.
Handles tracking and visualization of token usage through TruLens.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict

def create_token_trend(df: pd.DataFrame) -> go.Figure:
    """Create token usage trend visualization"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add total tokens line
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['total_tokens'],
            name="Total Tokens",
            line=dict(color="rgb(75, 192, 192)")
        ),
        secondary_y=False
    )

    # Add token cost line
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['estimated_cost'],
            name="Cost ($)",
            line=dict(color="rgb(255, 159, 64)")
        ),
        secondary_y=True
    )

    fig.update_layout(
        title="Token Usage and Cost Over Time",
        xaxis_title="Time",
        yaxis_title="Token Count",
        yaxis2_title="Cost ($)"
    )

    return fig

def display_token_metrics(token_df: pd.DataFrame):
    """
    Display token usage metrics with TruLens integration.

    Args:
        token_df: DataFrame containing token usage data from TruLens
    """
    if token_df.empty:
        st.info("No token usage data available yet. Start chatting to generate data!")
        return

    st.subheader("🔤 Token Usage Analysis")

    # Calculate token usage metrics
    total_tokens = token_df['total_tokens'].sum()
    prompt_tokens = token_df['prompt_tokens'].sum() if 'prompt_tokens' in token_df.columns else 0
    completion_tokens = token_df['completion_tokens'].sum() if 'completion_tokens' in token_df.columns else 0

    # Calculate costs (based on Mistral's pricing)
    prompt_cost = (prompt_tokens / 1000) * 0.7  # $0.7 per 1K tokens for input
    completion_cost = (completion_tokens / 1000) * 2.0  # $2.0 per 1K tokens for output
    total_cost = prompt_cost + completion_cost

    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Tokens",
            f"{total_tokens:,}",
            help="Total tokens used across all interactions"
        )

    with col2:
        avg_tokens = total_tokens / len(token_df) if len(token_df) > 0 else 0
        st.metric(
            "Avg Tokens/Query",
            f"{avg_tokens:.0f}",
            help="Average tokens per interaction"
        )

    with col3:
        completion_ratio = completion_tokens / total_tokens * 100 if total_tokens > 0 else 0
        st.metric(
            "Completion Ratio",
            f"{completion_ratio:.1f}%",
            help="Percentage of tokens used for completions"
        )

    with col4:
        st.metric(
            "Total Cost",
            f"${total_cost:.2f}",
            help="Total cost based on Mistral's pricing"
        )

    # Token Usage Trends
    with st.expander("📈 Usage Trends", expanded=True):
        token_df['estimated_cost'] = (
            (token_df['prompt_tokens'] / 1000 * 0.7) +
            (token_df['completion_tokens'] / 1000 * 2.0)
        )
        fig = create_token_trend(token_df)
        st.plotly_chart(fig, use_container_width=True)

    # Detailed Analysis
    with st.expander("📊 Usage Breakdown"):
        st.markdown("### Token Distribution")

        token_dist = pd.DataFrame({
            'Category': ['Prompt Tokens', 'Completion Tokens'],
            'Count': [prompt_tokens, completion_tokens],
            'Cost': [prompt_cost, completion_cost]
        })

        st.dataframe(
            token_dist.style.format({
                'Count': '{:,.0f}',
                'Cost': '${:.2f}'
            })
        )

        # Additional usage statistics
        st.markdown("### Usage Statistics")
        usage_stats = token_df[['total_tokens', 'prompt_tokens', 'completion_tokens']].describe()
        st.dataframe(
            usage_stats.style.format('{:,.1f}')
        )

def get_token_usage_summary(token_df: pd.DataFrame) -> Dict:
    """
    Generate summary of token usage metrics.

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

    prompt_cost = (prompt_tokens / 1000) * 0.7
    completion_cost = (completion_tokens / 1000) * 2.0
    total_cost = prompt_cost + completion_cost

    return {
        'total_tokens': total_tokens,
        'prompt_tokens': prompt_tokens,
        'completion_tokens': completion_tokens,
        'avg_tokens_per_query': total_tokens / len(token_df) if len(token_df) > 0 else 0,
        'completion_ratio': completion_tokens / total_tokens if total_tokens > 0 else 0,
        'total_cost': total_cost,
        'cost_per_token': total_cost / total_tokens if total_tokens > 0 else 0
    }