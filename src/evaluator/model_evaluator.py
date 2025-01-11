"""
Model evaluation component for the evaluation dashboard.
Handles model configuration comparison and guardrails using TruLens.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict

from trulens.core import TruSession
from trulens.connectors.snowflake import SnowflakeConnector
from trulens.core.guardrails.base import context_filter


def create_radar_chart(eval_df: pd.DataFrame) -> go.Figure:
    """Create radar chart for model comparison"""
    metrics = ['Groundedness', 'Context Relevance', 'Answer Relevance']

    fig = go.Figure()

    for config in eval_df['config_name'].unique():
        config_data = eval_df[eval_df['config_name'] == config]

        fig.add_trace(go.Scatterpolar(
            r=[config_data[metric].mean() for metric in metrics],
            theta=metrics,
            fill='toself',
            name=config
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True
    )

    return fig


def display_model_evaluation(eval_df: pd.DataFrame, snowpark_session=None):
    """
    Display model evaluation results and guardrails analysis.

    Args:
        eval_df: DataFrame containing evaluation results
        snowpark_session: Optional Snowpark session for TruLens
    """
    st.subheader("📊 Model Evaluation & Guardrails")

    # Initialize TruLens if session provided
    if snowpark_session:
        tru_connector = SnowflakeConnector(snowpark_session=snowpark_session)
        tru = TruSession(connector=tru_connector)

    # Model Configuration Section
    with st.expander("⚙️ Model Configuration", expanded=True):
        st.markdown("### Current Configuration")

        col1, col2, col3 = st.columns(3)
        with col1:
            context_window = st.number_input(
                "Context Window Size",
                min_value=1,
                max_value=10,
                value=4
            )
        with col2:
            relevance_threshold = st.slider(
                "Relevance Threshold",
                min_value=0.0,
                max_value=1.0,
                value=0.75,
                help="Minimum relevance score for context filtering"
            )
        with col3:
            max_tokens = st.number_input(
                "Max Response Tokens",
                min_value=100,
                max_value=2000,
                value=500
            )

    # Model Comparison
    if not eval_df.empty:
        st.markdown("### Model Performance Comparison")

        fig = create_radar_chart(eval_df)
        st.plotly_chart(fig, use_container_width=True)

        # Detailed Metrics Table
        st.markdown("### Detailed Metrics")
        metrics_summary = get_evaluation_summary(eval_df)

        for config, metrics in metrics_summary.items():
            st.markdown(f"**Configuration: {config}**")
            metrics_df = pd.DataFrame(metrics['metrics']).T
            st.dataframe(
                metrics_df.style.format({
                    'mean': '{:.2%}',
                    'std': '{:.2%}',
                    'min': '{:.2%}',
                    'max': '{:.2%}'
                })
            )

    # Guardrails Analysis
    with st.expander("🛡️ Guardrails Analysis", expanded=True):
        st.markdown("### Context Filtering Guardrails")

        if not eval_df.empty:
            filtered_stats = analyze_filtering_impact(eval_df, relevance_threshold)

            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Filtered Context Chunks",
                    f"{filtered_stats['filtered_chunks']}",
                    help="Number of context chunks filtered out"
                )
            with col2:
                st.metric(
                    "Quality Improvement",
                    f"{filtered_stats['quality_improvement']:+.1%}",
                    help="Improvement in response quality after filtering"
                )

            # Filtering Impact Visualization
            fig = create_filtering_impact_chart(filtered_stats)
            st.plotly_chart(fig, use_container_width=True)


def analyze_filtering_impact(eval_df: pd.DataFrame, threshold: float) -> Dict:
    """Analyze impact of context filtering"""
    # Simulate filtering impact
    filtered_chunks = len(eval_df[eval_df['Context Relevance'] < threshold])

    # Calculate quality metrics
    quality_before = eval_df['Answer Relevance'].mean()
    quality_after = eval_df[eval_df['Context Relevance'] >= threshold]['Answer Relevance'].mean()

    return {
        'filtered_chunks': filtered_chunks,
        'quality_improvement': quality_after - quality_before if not pd.isna(quality_after) else 0,
        'threshold': threshold,
        'before_metrics': {
            'relevance': quality_before,
            'groundedness': eval_df['Groundedness'].mean()
        },
        'after_metrics': {
            'relevance': quality_after,
            'groundedness': eval_df[eval_df['Context Relevance'] >= threshold]['Groundedness'].mean()
        }
    }


def create_filtering_impact_chart(stats: Dict) -> go.Figure:
    """Create visualization of filtering impact"""
    metrics = ['relevance', 'groundedness']
    before_values = [stats['before_metrics'][m] for m in metrics]
    after_values = [stats['after_metrics'][m] for m in metrics]

    fig = go.Figure(data=[
        go.Bar(name='Before Filtering', x=metrics, y=before_values),
        go.Bar(name='After Filtering', x=metrics, y=after_values)
    ])

    fig.update_layout(
        title="Impact of Context Filtering",
        barmode='group',
        yaxis_title="Score",
        yaxis_tickformat=',.0%'
    )

    return fig


def get_evaluation_summary(eval_df: pd.DataFrame) -> Dict:
    """Generate evaluation summary for each configuration"""
    summary = {}

    for config in eval_df['config_name'].unique():
        config_data = eval_df[eval_df['config_name'] == config]

        summary[config] = {
            'metrics': {
                metric: {
                    'mean': config_data[metric].mean(),
                    'std': config_data[metric].std(),
                    'min': config_data[metric].min(),
                    'max': config_data[metric].max()
                }
                for metric in ['Groundedness', 'Context Relevance', 'Answer Relevance']
            },
            'total_queries': len(config_data),
            'timestamp': config_data['timestamp'].max()
        }

    return summary