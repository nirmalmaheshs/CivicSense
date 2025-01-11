"""
Data loading utilities for the evaluation dashboard.
These functions handle loading and processing data from Streamlit session state.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional


def load_metrics_data() -> pd.DataFrame:
    """
    Load and process metrics history data from session state.
    Returns:
        pd.DataFrame: DataFrame containing metrics data or empty DataFrame if no data exists
    """
    if 'metrics_history' in st.session_state and st.session_state.metrics_history:
        # Create list of dictionaries with flattened metadata
        data_list = []
        for m in st.session_state.metrics_history:
            entry = {k: v for k, v in m.items() if k != 'metadata'}
            if 'metadata' in m and m['metadata']:
                # Extract query and response from metadata
                entry['question'] = m['metadata'].get('query', 'N/A')
                entry['answer'] = m['metadata'].get('response', 'N/A')
            data_list.append(entry)

        metrics_df = pd.DataFrame(data_list)
        metrics_df['timestamp'] = pd.to_datetime(metrics_df['timestamp'])
        return metrics_df
    return pd.DataFrame()


def load_token_data() -> pd.DataFrame:
    """
    Load token usage data from session state.
    Returns:
        pd.DataFrame: DataFrame containing token usage data or empty DataFrame if no data exists
    """
    if 'token_usage' in st.session_state and st.session_state.token_usage:
        token_df = pd.DataFrame(st.session_state.token_usage)
        token_df['timestamp'] = pd.to_datetime(token_df['timestamp'])
        return token_df
    return pd.DataFrame()


def load_latency_data() -> pd.DataFrame:
    """
    Load latency tracking data from session state.
    Returns:
        pd.DataFrame: DataFrame containing latency data or empty DataFrame if no data exists
    """
    if 'latency_tracking' in st.session_state and st.session_state.latency_tracking:
        latency_df = pd.DataFrame(st.session_state.latency_tracking)
        latency_df['timestamp'] = pd.to_datetime(latency_df['timestamp'])
        return latency_df
    return pd.DataFrame()


def load_cost_data() -> pd.DataFrame:
    """
    Load cost tracking data from session state.
    Returns:
        pd.DataFrame: DataFrame containing cost data or empty DataFrame if no data exists
    """
    if 'cost_tracking' in st.session_state and st.session_state.cost_tracking:
        cost_df = pd.DataFrame(st.session_state.cost_tracking)
        cost_df['timestamp'] = pd.to_datetime(cost_df['timestamp'])
        return cost_df
    return pd.DataFrame()


def load_evaluation_results() -> pd.DataFrame:
    """
    Load model evaluation results from session state.
    Returns:
        pd.DataFrame: DataFrame containing evaluation results or empty DataFrame if no data exists
    """
    if 'evaluation_results' in st.session_state and st.session_state.evaluation_results:
        eval_df = pd.DataFrame(st.session_state.evaluation_results)
        eval_df['timestamp'] = pd.to_datetime(eval_df['timestamp'])
        return eval_df
    return pd.DataFrame()


def get_recent_data(df: pd.DataFrame, hours: int = 24) -> pd.DataFrame:
    """
    Filter DataFrame to get only recent data within specified hours.

    Args:
        df (pd.DataFrame): Input DataFrame with 'timestamp' column
        hours (int): Number of hours to look back

    Returns:
        pd.DataFrame: Filtered DataFrame containing only recent data
    """
    if df.empty:
        return df
    cutoff = pd.Timestamp.now() - timedelta(hours=hours)
    return df[df['timestamp'] > cutoff]


def load_all_metrics() -> Dict[str, pd.DataFrame]:
    """
    Load all available metrics data.

    Returns:
        Dict[str, pd.DataFrame]: Dictionary containing all metrics DataFrames
            Keys: 'metrics', 'tokens', 'latency', 'cost', 'evaluation'
    """
    return {
        'metrics': load_metrics_data(),
        'tokens': load_token_data(),
        'latency': load_latency_data(),
        'cost': load_cost_data(),
        'evaluation': load_evaluation_results()
    }


def prepare_export_data(df: pd.DataFrame, name: str) -> Optional[bytes]:
    """
    Prepare DataFrame for export as CSV.

    Args:
        df (pd.DataFrame): DataFrame to export
        name (str): Name of the metric for filename

    Returns:
        Optional[bytes]: CSV data as bytes if DataFrame is not empty, None otherwise
    """
    if not df.empty:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_metrics_{timestamp}.csv"
        return df.to_csv(index=False).encode('utf-8'), filename
    return None


def aggregate_daily_metrics(df: pd.DataFrame, value_column: str) -> pd.DataFrame:
    """
    Aggregate metrics by day for trending analysis.

    Args:
        df (pd.DataFrame): Input DataFrame with 'timestamp' column
        value_column (str): Column to aggregate

    Returns:
        pd.DataFrame: Daily aggregated metrics
    """
    if df.empty:
        return df
    return (df.set_index('timestamp')
            .resample('D')[value_column]
            .agg(['mean', 'min', 'max', 'count'])
            .reset_index())