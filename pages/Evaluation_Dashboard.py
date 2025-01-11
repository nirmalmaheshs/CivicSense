"""
RAG Evaluation Dashboard
A comprehensive dashboard for monitoring and analyzing RAG system performance.
"""

import streamlit as st
from datetime import datetime

# Import data loaders
from src.dashboard.data_loaders import (
    load_metrics_data,
    load_token_data,
    load_latency_data,
    load_cost_data,
    load_evaluation_results
)

# Import components
from src.dashboard.components import (
    display_performance_metrics,
    display_token_metrics,
    display_latency_metrics,
    display_cost_metrics,
    display_model_evaluation
)

# Page configuration
st.set_page_config(
    page_title="RAG Evaluation Dashboard",
    page_icon="📊",
    layout="wide"
)


def initialize_dashboard():
    """Initialize the dashboard state and load data"""
    # Initialize chatbot if needed
    if 'chatbot' not in st.session_state:
        from app import initialize_app
        chatbot = initialize_app()
        st.success("Chatbot initialized successfully!")

    # Load all required data
    metrics_df = load_metrics_data()
    token_df = load_token_data()
    latency_df = load_latency_data()
    cost_df = load_cost_data()
    eval_df = load_evaluation_results()

    return metrics_df, token_df, latency_df, cost_df, eval_df


def main():
    """Main dashboard function"""
    # Dashboard title
    st.title("RAG Evaluation Dashboard 📊")
    st.markdown("""
    Monitor and analyze the performance of your RAG system with comprehensive metrics and visualizations.
    """)

    # Initialize data
    metrics_df, token_df, latency_df, cost_df, eval_df = initialize_dashboard()

    # Create tabs for different sections
    tabs = st.tabs([
        "🎯 Performance",
        "🔤 Token Usage",
        "⚡ Latency",
        "💰 Cost Analysis",
        "📈 Model Evaluation"
    ])

    # Performance Metrics Tab
    with tabs[0]:
        display_performance_metrics(metrics_df)

    # Token Usage Tab
    with tabs[1]:
        display_token_metrics(token_df)

    # Latency Analysis Tab
    with tabs[2]:
        display_latency_metrics(latency_df)

    # Cost Analysis Tab
    with tabs[3]:
        display_cost_metrics(cost_df)

    # Model Evaluation Tab
    with tabs[4]:
        display_model_evaluation(
            eval_df,
            st.session_state.chatbot if 'chatbot' in st.session_state else None
        )

    # Sidebar - Export functionality
    with st.sidebar:
        st.title("Export Data")
        export_options = {
            "Performance Metrics": metrics_df,
            "Token Usage": token_df,
            "Latency Data": latency_df,
            "Cost Analysis": cost_df,
            "Model Evaluation": eval_df
        }

        if st.button("Export All Data"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            for name, df in export_options.items():
                if not df.empty:
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label=f"Download {name}",
                        data=csv,
                        file_name=f'{name.lower().replace(" ", "_")}_{timestamp}.csv',
                        mime='text/csv',
                        key=f'download_{name.lower().replace(" ", "_")}'
                    )

        # Dashboard Info
        st.markdown("---")
        st.markdown("""
        ### 📋 Dashboard Guide

        - **Performance**: Overall system performance metrics
        - **Token Usage**: Token consumption and costs
        - **Latency**: Response time analysis
        - **Cost Analysis**: Cost tracking and trends
        - **Model Evaluation**: Model configuration comparison

        Use the tabs above to navigate between different metrics.
        """)

        # Refresh Data
        if st.button("🔄 Refresh Data"):
            st.rerun()


if __name__ == "__main__":
    main()