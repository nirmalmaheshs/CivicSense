"""
Model evaluation component for the evaluation dashboard.
Handles model configuration comparison, evaluation, and analysis.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, Optional
from ..visualizations import create_model_comparison_radar


def display_model_evaluation(eval_df: pd.DataFrame, chatbot: Optional[object] = None):
    """
    Display the model evaluation section.

    Args:
        eval_df: DataFrame containing evaluation results
        chatbot: Optional chatbot instance for running new evaluations
    """
    st.header("Model Configuration Analysis")

    # New Evaluation Section
    with st.expander("🔄 Run New Evaluation", expanded=False):
        run_new_evaluation(chatbot)

    if eval_df.empty:
        st.info("No evaluation results available yet. Run an evaluation to see comparisons!")
        return

    display_evaluation_results(eval_df)


def run_new_evaluation(chatbot: Optional[object]):
    """
    Interface for running new model evaluations.

    Args:
        chatbot: Chatbot instance for running evaluations
    """
    config_name = st.text_input(
        "Configuration Name",
        placeholder="e.g., Base Model, Improved Context, etc."
    )

    col1, col2 = st.columns(2)
    with col1:
        context_window = st.number_input(
            "Context Window Size",
            min_value=1,
            max_value=10,
            value=4,
            help="Number of context chunks to retrieve"
        )
        temperature = st.slider(
            "Temperature",
            0.0,
            1.0,
            0.7,
            0.1,
            help="Controls randomness in response generation"
        )

    with col2:
        top_p = st.slider(
            "Top P",
            0.0,
            1.0,
            0.9,
            0.1,
            help="Controls diversity of token selection"
        )
        max_tokens = st.number_input(
            "Max Tokens",
            min_value=100,
            max_value=2000,
            value=500,
            help="Maximum tokens in response"
        )

    config_details = {
        'context_window': context_window,
        'temperature': temperature,
        'top_p': top_p,
        'max_tokens': max_tokens,
        'timestamp': datetime.now().isoformat()
    }

    if st.button("Run Evaluation"):
        if not config_name:
            st.warning("Please provide a configuration name.")
            return

        if not chatbot:
            st.error("Chatbot not initialized. Please return to the main page.")
            return

        with st.spinner("Evaluating model with current configuration..."):
            try:
                results = chatbot.model_evaluator.evaluate_model(
                    chatbot,
                    config_name,
                    config_details
                )
                st.success(f"Evaluation completed for configuration: {config_name}")
            except Exception as e:
                st.error(f"Error during evaluation: {str(e)}")


def display_evaluation_results(eval_df: pd.DataFrame):
    """
    Display evaluation results and comparisons.

    Args:
        eval_df: DataFrame containing evaluation results
    """
    metrics = [
        'answer_similarity', 'factual_accuracy', 'context_relevance',
        'response_relevance', 'completion_quality'
    ]

    # Configuration Comparison
    st.subheader("📊 Configuration Comparison")
    fig = create_model_comparison_radar(eval_df, metrics)
    st.plotly_chart(fig, use_container_width=True)

    # Configuration Selection
    selected_config = st.selectbox(
        "Select configuration to analyze:",
        options=eval_df['config_name'].unique()
    )

    if selected_config:
        display_configuration_details(eval_df, selected_config, metrics)


def display_configuration_details(eval_df: pd.DataFrame, config_name: str, metrics: list):
    """
    Display detailed analysis for a specific configuration.

    Args:
        eval_df: DataFrame containing evaluation results
        config_name: Name of selected configuration
        metrics: List of metrics to analyze
    """
    config_data = eval_df[eval_df['config_name'] == config_name]

    # Configuration Settings
    st.markdown("### ⚙️ Configuration Settings")
    config_details = {k: v for k, v in config_data.iloc[0].items()
                      if k in ['context_window', 'temperature', 'top_p', 'max_tokens']}
    st.json(config_details)

    # Performance Metrics
    st.markdown("### 📈 Performance Metrics")
    metric_cols = st.columns(len(metrics))
    for col, metric in zip(metric_cols, metrics):
        with col:
            value = config_data[metric].mean()
            std = config_data[metric].std()
            st.metric(
                metric.replace('_', ' ').title(),
                f"{value:.2f}",
                f"±{std:.2f}",
                help=f"Mean ± Standard Deviation"
            )

    # Detailed Results
    with st.expander("📝 Detailed Results"):
        st.markdown("### Question-wise Performance")
        for _, row in config_data.iterrows():
            with st.container():
                st.markdown(f"**Question:** {row['question']}")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Ground Truth:**")
                    st.info(row['ground_truth'])
                with col2:
                    st.markdown("**Model Response:**")
                    st.info(row['model_response'])

                metric_cols = st.columns(len(metrics))
                for col, metric in zip(metric_cols, metrics):
                    with col:
                        st.metric(
                            metric.replace('_', ' ').title(),
                            f"{row[metric]:.2f}"
                        )
                st.markdown("---")

    # Export Options
    if st.button(f"Export Results for {config_name}"):
        export_results(config_data, config_name)


def export_results(config_data: pd.DataFrame, config_name: str):
    """
    Export configuration results as CSV.

    Args:
        config_data: DataFrame containing configuration results
        config_name: Name of the configuration
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv = config_data.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f'{config_name}_results_{timestamp}.csv',
        mime='text/csv'
    )


def get_evaluation_summary(eval_df: pd.DataFrame) -> Dict:
    """
    Generate a summary of evaluation results.

    Args:
        eval_df: DataFrame containing evaluation results

    Returns:
        dict: Summary statistics for each configuration
    """
    if eval_df.empty:
        return {}

    metrics = [
        'answer_similarity', 'factual_accuracy', 'context_relevance',
        'response_relevance', 'completion_quality'
    ]

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
                } for metric in metrics
            },
            'timestamp': config_data['timestamp'].max(),
            'total_evaluations': len(config_data)
        }

    return summary