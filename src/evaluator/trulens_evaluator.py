import pandas as pd
import streamlit as st
from typing import Dict, List

from trulens.core import TruSession
from trulens.connectors.snowflake import SnowflakeConnector
from trulens.providers.cortex.provider import Cortex
from trulens.core import Feedback
from trulens.core import Select
from snowflake.snowpark.context import get_active_session


class TruLensEvaluator:
    def __init__(self):
        # Initialize Snowflake session
        self.session = get_active_session()

        # Setup TruLens with Snowflake
        self.connector = SnowflakeConnector(snowpark_session=self.session)
        self.tru = TruSession(connector=self.connector)

        # Initialize Cortex provider
        self.provider = Cortex(snowpark_session=self.session, model_engine="mistral-large2")

    def get_feedback_functions(self) -> List[Feedback]:
        """Get feedback functions for evaluation"""
        # Groundedness feedback
        f_groundedness = (
            Feedback(
                self.provider.groundedness_measure_with_cot_reasons,
                name="Groundedness"
            )
            .on(Select.RecordCalls.retrieve_context.rets[:].collect())
            .on_output()
        )

        # Context relevance feedback
        f_context_relevance = (
            Feedback(
                self.provider.context_relevance,
                name="Context Relevance"
            )
            .on(Select.RecordCalls.retrieve_context.rets[:].collect())
            .on_output()
        )

        # Answer relevance feedback
        f_answer_relevance = (
            Feedback(
                self.provider.answer_relevance,
                name="Answer Relevance"
            )
            .on_input()
            .on_output()
        )

        return [f_groundedness, f_context_relevance, f_answer_relevance]

    def get_metrics(self) -> Dict:
        """Get evaluation metrics from TruLens"""
        try:
            # Get leaderboard data
            leaderboard = self.tru.get_leaderboard()

            if leaderboard.empty:
                return {
                    "groundedness": 0.0,
                    "context_relevance": 0.0,
                    "answer_relevance": 0.0
                }

            # Calculate metrics
            metrics = {
                "groundedness": leaderboard["Groundedness"].mean(),
                "context_relevance": leaderboard["Context Relevance"].mean(),
                "answer_relevance": leaderboard["Answer Relevance"].mean()
            }

            return metrics

        except Exception as e:
            st.error(f"Error getting metrics: {str(e)}")
            return {
                "groundedness": 0.0,
                "context_relevance": 0.0,
                "answer_relevance": 0.0
            }

    def get_detailed_metrics(self) -> pd.DataFrame:
        """Get detailed metrics for dashboard"""
        try:
            # Get full records
            records = self.tru.get_records()

            if not records:
                return pd.DataFrame()

            # Transform records into DataFrame with timestamps
            metrics_data = []
            for record in records:
                metric_entry = {
                    "timestamp": record.timestamp,
                    "query": record.input,
                    "response": record.output
                }

                # Add feedback scores
                for feedback in record.feedback_results:
                    metric_entry[feedback.name] = feedback.score

                metrics_data.append(metric_entry)

            return pd.DataFrame(metrics_data)

        except Exception as e:
            st.error(f"Error getting detailed metrics: {str(e)}")
            return pd.DataFrame()

    def analyze_performance(self) -> Dict:
        """Analyze RAG performance trends"""
        metrics_df = self.get_detailed_metrics()

        if metrics_df.empty:
            return {}

        # Get overall stats
        stats = {}
        for metric in ["Groundedness", "Context Relevance", "Answer Relevance"]:
            if metric in metrics_df.columns:
                stats[metric.lower().replace(" ", "_")] = {
                    "average": metrics_df[metric].mean(),
                    "std": metrics_df[metric].std(),
                    "min": metrics_df[metric].min(),
                    "max": metrics_df[metric].max(),
                    "recent_trend": metrics_df[metric].tail(10).mean()
                }

        # Add query analysis
        if "query" in metrics_df.columns:
            stats["queries"] = {
                "total": len(metrics_df),
                "unique": metrics_df["query"].nunique(),
                "avg_length": metrics_df["query"].str.len().mean()
            }

        return stats