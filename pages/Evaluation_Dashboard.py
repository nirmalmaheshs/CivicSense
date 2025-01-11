import streamlit as st
import pandas as pd

from src.dashboard.components import (
    display_performance_metrics,
    display_token_metrics,
    display_latency_metrics,
    display_model_evaluation
)
from snowflake.snowpark.context import get_active_session
from src.utils import get_tru_lens_session


def main():
    st.set_page_config(layout="wide", page_title="RAG Evaluation Dashboard")
    st.title("RAG Evaluation Dashboard 📊")

    # Initialize TruLens
    tru_session = get_tru_lens_session()

    # Get evaluation data
    records_df = pd.DataFrame(tru_session.get_leaderboard())

    # Create tabs for different metrics
    tabs = st.tabs([
        "🎯 Performance",
        "🔤 Token Usage",
        "⚡ Latency",
        "📈 Model Evaluation"
    ])

    with tabs[0]:
        display_performance_metrics(records_df)

    with tabs[1]:
        display_token_metrics(records_df)

    with tabs[2]:
        display_latency_metrics(records_df)

    with tabs[3]:
        display_model_evaluation(records_df, get_active_session())

    # Export functionality
    with st.sidebar:
        st.title("Export Data")
        if st.button("Download Evaluation Data"):
            csv = records_df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                "rag_evaluation.csv",
                "text/csv"
            )

if __name__ == "__main__":
    main()