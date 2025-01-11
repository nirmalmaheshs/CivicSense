import pandas as pd
import streamlit as st
from typing import Dict


class EnhancedMetrics:
    def __init__(self):
        # Initialize tracking for additional metrics
        if 'cost_tracking' not in st.session_state:
            st.session_state.cost_tracking = []
        if 'latency_tracking' not in st.session_state:
            st.session_state.latency_tracking = []
        if 'token_usage' not in st.session_state:
            st.session_state.token_usage = []

    def track_interaction(self, prompt_tokens: int, completion_tokens: int,
                          latency_ms: float, cost: float):
        """Track a new interaction with its metrics"""
        timestamp = pd.Timestamp.now().isoformat()

        # Token usage tracking
        token_data = {
            'timestamp': timestamp,
            'prompt_tokens': int(prompt_tokens),
            'completion_tokens': int(completion_tokens),
            'total_tokens': int(prompt_tokens + completion_tokens),
            'token_ratio': float(completion_tokens) / float(max(1, prompt_tokens))
        }
        st.session_state.token_usage.append(token_data)

        # Latency tracking
        latency_data = {
            'timestamp': timestamp,
            'latency_ms': float(latency_ms),
            'latency_seconds': float(latency_ms) / 1000.0
        }
        st.session_state.latency_tracking.append(latency_data)

        # Cost tracking
        cost_data = {
            'timestamp': timestamp,
            'cost': float(cost),
            'cost_per_token': float(cost) / float(max(1, prompt_tokens + completion_tokens))
        }
        st.session_state.cost_tracking.append(cost_data)

    def get_token_metrics(self) -> Dict:
        """Get token usage metrics"""
        if not st.session_state.token_usage:
            return {
                'total_tokens': 0,
                'avg_token_ratio': 0,
                'total_prompt_tokens': 0,
                'total_completion_tokens': 0
            }

        df = pd.DataFrame(st.session_state.token_usage)
        return {
            'total_tokens': int(df['total_tokens'].sum()),
            'avg_token_ratio': float(df['token_ratio'].mean()),
            'total_prompt_tokens': int(df['prompt_tokens'].sum()),
            'total_completion_tokens': int(df['completion_tokens'].sum())
        }

    def get_latency_metrics(self) -> Dict:
        """Get latency metrics"""
        if not st.session_state.latency_tracking:
            return {
                'avg_latency_ms': 0,
                'max_latency_ms': 0,
                'min_latency_ms': 0,
                'total_requests': 0
            }

        df = pd.DataFrame(st.session_state.latency_tracking)
        return {
            'avg_latency_ms': float(df['latency_ms'].mean()),
            'max_latency_ms': float(df['latency_ms'].max()),
            'min_latency_ms': float(df['latency_ms'].min()),
            'total_requests': len(df)
        }

    def get_cost_metrics(self) -> Dict:
        """Get cost metrics"""
        if not st.session_state.cost_tracking:
            return {
                'total_cost': 0,
                'avg_cost_per_request': 0,
                'avg_cost_per_token': 0
            }

        df = pd.DataFrame(st.session_state.cost_tracking)
        return {
            'total_cost': float(df['cost'].sum()),
            'avg_cost_per_request': float(df['cost'].mean()),
            'avg_cost_per_token': float(df['cost_per_token'].mean())
        }

    def get_all_metrics(self) -> Dict:
        """Get all metrics in a single dictionary"""
        return {
            'token_metrics': self.get_token_metrics(),
            'latency_metrics': self.get_latency_metrics(),
            'cost_metrics': self.get_cost_metrics()
        }

    def display_detailed_metrics(self):
        """Display detailed metrics in Streamlit"""
        metrics = self.get_all_metrics()

        st.sidebar.subheader("📊 Detailed Metrics")

        # Token Usage
        with st.sidebar.expander("Token Usage"):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Tokens", f"{metrics['token_metrics']['total_tokens']:,}")
                st.metric("Total Prompt Tokens", f"{metrics['token_metrics']['total_prompt_tokens']:,}")
            with col2:
                st.metric("Avg Token Ratio", f"{metrics['token_metrics']['avg_token_ratio']:.2f}")
                st.metric("Total Completion Tokens", f"{metrics['token_metrics']['total_completion_tokens']:,}")

        # Latency
        with st.sidebar.expander("Latency"):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Avg Latency", f"{metrics['latency_metrics']['avg_latency_ms']:.0f}ms")
                st.metric("Min Latency", f"{metrics['latency_metrics']['min_latency_ms']:.0f}ms")
            with col2:
                st.metric("Max Latency", f"{metrics['latency_metrics']['max_latency_ms']:.0f}ms")
                st.metric("Total Requests", metrics['latency_metrics']['total_requests'])

        # Cost
        with st.sidebar.expander("Cost"):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Cost", f"${metrics['cost_metrics']['total_cost']:.4f}")
                st.metric("Avg Cost/Request", f"${metrics['cost_metrics']['avg_cost_per_request']:.4f}")
            with col2:
                st.metric("Avg Cost/Token", f"${metrics['cost_metrics']['avg_cost_per_token']:.6f}")

    def get_metrics_history(self) -> pd.DataFrame:
        """Get metrics history as a DataFrame"""
        token_df = pd.DataFrame(st.session_state.token_usage)
        latency_df = pd.DataFrame(st.session_state.latency_tracking)
        cost_df = pd.DataFrame(st.session_state.cost_tracking)

        # Merge all metrics based on timestamp
        df = pd.merge(token_df, latency_df, on='timestamp', how='outer')
        df = pd.merge(df, cost_df, on='timestamp', how='outer')

        return df.sort_values('timestamp', ascending=False)