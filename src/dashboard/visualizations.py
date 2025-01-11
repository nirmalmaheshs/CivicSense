"""
Visualization utilities for the evaluation dashboard.
Contains functions for creating various plots and charts using Plotly.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict

# Color schemes for consistent visualization
COLORS = {
    'primary': ['#2E86C1', '#28B463', '#CB4335'],  # Blue, Green, Red
    'secondary': ['#85C1E9', '#82E0AA', '#F1948A'],  # Lighter shades
    'neutral': ['#566573', '#808B96', '#ABB2B9']  # Grays
}


def create_performance_trend(metrics_df: pd.DataFrame, metrics: List[str]) -> go.Figure:
    """
    Create line chart showing performance metrics over time.

    Args:
        metrics_df: DataFrame with timestamp and metric columns
        metrics: List of metric names to plot

    Returns:
        Plotly figure object
    """
    fig = go.Figure()

    for metric, color in zip(metrics, COLORS['primary']):
        fig.add_trace(
            go.Scatter(
                x=metrics_df['timestamp'],
                y=metrics_df[metric],
                name=metric.replace('_', ' ').title(),
                line=dict(color=color),
                mode='lines+markers'
            )
        )

    fig.update_layout(
        title="Performance Metrics Over Time",
        xaxis_title="Time",
        yaxis_title="Score",
        yaxis_range=[0, 1],
        height=400,
        template="plotly_white",
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    return fig


def create_score_distribution(metrics_df: pd.DataFrame, metrics: List[str]) -> go.Figure:
    """
    Create violin plot showing distribution of scores.

    Args:
        metrics_df: DataFrame with metric columns
        metrics: List of metric names to plot

    Returns:
        Plotly figure object
    """
    fig = go.Figure()

    for metric, color in zip(metrics, COLORS['primary']):
        fig.add_trace(
            go.Violin(
                y=metrics_df[metric],
                name=metric.replace('_', ' ').title(),
                box_visible=True,
                meanline_visible=True,
                fillcolor=color,
                line_color=color,
                opacity=0.7
            )
        )

    fig.update_layout(
        title="Score Distributions",
        yaxis_title="Score",
        height=400,
        template="plotly_white",
        showlegend=True,
        yaxis_range=[0, 1],
        violinmode='group'
    )
    return fig


def create_token_usage_trend(token_df: pd.DataFrame) -> go.Figure:
    """
    Create stacked area chart of token usage over time.

    Args:
        token_df: DataFrame with timestamp and token columns

    Returns:
        Plotly figure object
    """
    fig = go.Figure()

    for token_type, color in zip(['prompt_tokens', 'completion_tokens'],
                                 COLORS['primary']):
        fig.add_trace(
            go.Scatter(
                x=token_df['timestamp'],
                y=token_df[token_type],
                name=token_type.replace('_', ' ').title(),
                stackgroup='one',
                line=dict(color=color)
            )
        )

    fig.update_layout(
        title="Token Usage Over Time",
        xaxis_title="Time",
        yaxis_title="Token Count",
        height=400,
        template="plotly_white",
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    return fig


def create_latency_trend(latency_df: pd.DataFrame) -> go.Figure:
    """
    Create scatter plot with trend line for latency.

    Args:
        latency_df: DataFrame with timestamp and latency_ms columns

    Returns:
        Plotly figure object
    """
    fig = go.Figure()

    # Individual points
    fig.add_trace(
        go.Scatter(
            x=latency_df['timestamp'],
            y=latency_df['latency_ms'],
            mode='markers',
            name='Response Time',
            marker=dict(
                size=8,
                color=COLORS['primary'][0],
                opacity=0.6
            )
        )
    )

    # Moving average
    window = max(1, len(latency_df) // 10)  # Dynamic window size
    ma = latency_df['latency_ms'].rolling(window=window).mean()

    fig.add_trace(
        go.Scatter(
            x=latency_df['timestamp'],
            y=ma,
            mode='lines',
            name=f'{window}-Point Moving Average',
            line=dict(
                color=COLORS['primary'][1],
                width=2
            )
        )
    )

    fig.update_layout(
        title="Response Latency Over Time",
        xaxis_title="Time",
        yaxis_title="Latency (ms)",
        height=400,
        template="plotly_white",
        hovermode='x unified',
        showlegend=True
    )
    return fig


def create_cost_analysis(cost_df: pd.DataFrame) -> go.Figure:
    """
    Create combination chart showing daily cost bars and cumulative line.

    Args:
        cost_df: DataFrame with timestamp and cost columns

    Returns:
        Plotly figure object
    """
    fig = go.Figure()

    # Daily cost bars
    daily_cost = (cost_df.set_index('timestamp')
                  .resample('D')['cost']
                  .sum()
                  .reset_index())

    fig.add_trace(
        go.Bar(
            x=daily_cost['timestamp'],
            y=daily_cost['cost'],
            name='Daily Cost',
            marker_color=COLORS['primary'][0]
        )
    )

    # Cumulative cost line
    fig.add_trace(
        go.Scatter(
            x=cost_df['timestamp'],
            y=cost_df['cost'].cumsum(),
            name='Cumulative Cost',
            yaxis='y2',
            line=dict(
                color=COLORS['primary'][1],
                width=2
            )
        )
    )

    fig.update_layout(
        title="Cost Analysis Over Time",
        xaxis_title="Time",
        yaxis_title="Daily Cost ($)",
        yaxis2=dict(
            title="Cumulative Cost ($)",
            overlaying="y",
            side="right"
        ),
        height=400,
        template="plotly_white",
        hovermode='x unified',
        showlegend=True,
        barmode='relative'
    )
    return fig


def create_model_comparison_radar(eval_df: pd.DataFrame, metrics: List[str]) -> go.Figure:
    """
    Create radar chart comparing different model configurations.

    Args:
        eval_df: DataFrame with configuration and metric columns
        metrics: List of metrics to compare

    Returns:
        Plotly figure object
    """
    fig = go.Figure()

    for idx, config in enumerate(eval_df['config_name'].unique()):
        config_metrics = eval_df[eval_df['config_name'] == config][metrics].mean()
        color = COLORS['primary'][idx % len(COLORS['primary'])]

        fig.add_trace(
            go.Scatterpolar(
                r=config_metrics.values,
                theta=metrics,
                name=config,
                fill='toself',
                line=dict(color=color)
            )
        )

    fig.update_layout(
        title="Model Configuration Comparison",
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=True,
        template="plotly_white",
        height=400
    )
    return fig