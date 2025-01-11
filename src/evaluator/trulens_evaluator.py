import pandas as pd
import streamlit as st
from typing import List, Dict
from trulens_eval import Tru, Feedback
from snowflake.cortex import Complete

class TruLensEvaluator:
    def __init__(self):
        # Initialize TruLens
        self.tru = Tru()

        # Define feedback functions
        self.feedback_functions = [
            Feedback(
                self.context_relevance,
                name="Context Relevance",
                higher_is_better=True
            ),
            Feedback(
                self.response_relevance,
                name="Response Relevance",
                higher_is_better=True
            ),
            Feedback(
                self.completion_quality,
                name="Completion Quality",
                higher_is_better=True
            )
        ]

        # Initialize metrics storage
        if 'metrics_history' not in st.session_state:
            st.session_state.metrics_history = []

    def context_relevance(self, query: str, context: List[str]) -> float:
        """Evaluate relevance of retrieved context to the query."""
        prompt = f"""
        Query: {query}
        Context: {' '.join(context)}

        On a scale from 0 to 1, how relevant is the context to answering the query?
        Provide only the numerical score.
        """

        try:
            response = Complete("mistral-large2", prompt)
            score = float(response.strip())
            return min(max(score, 0), 1)
        except:
            return 0.0

    def response_relevance(self, query: str, response: str) -> float:
        """Evaluate relevance of the response to the query."""
        prompt = f"""
        Query: {query}
        Response: {response}

        On a scale from 0 to 1, how relevant and accurate is the response to the query?
        Provide only the numerical score.
        """

        try:
            score_response = Complete("mistral-large2", prompt)
            score = float(score_response.strip())
            return min(max(score, 0), 1)
        except:
            return 0.0

    def completion_quality(self, query: str, response: str) -> float:
        """Evaluate the overall quality of the completion."""
        prompt = f"""
        Query: {query}
        Response: {response}

        On a scale from 0 to 1, evaluate the quality of this response based on:
        - Clarity and coherence
        - Completeness of the answer
        - Professional tone
        - Factual accuracy (if verifiable from the response)

        Provide only the numerical score.
        """

        try:
            score_response = Complete("mistral-large2", prompt)
            score = float(score_response.strip())
            return min(max(score, 0), 1)
        except:
            return 0.0

    def log_feedback(self, query: str, context: List[str], response: str, metadata: Dict = None):
        """Log feedback for a single interaction"""
        if metadata is None:
            metadata = {}

        # Calculate feedback scores
        if context and response:
            context_rel = self.context_relevance(query, context)
            response_rel = self.response_relevance(query, response)
            completion_qual = self.completion_quality(query, response)

            # Store metrics
            metrics = {
                "timestamp": pd.Timestamp.now().isoformat(),
                "context_relevance": float(context_rel),
                "response_relevance": float(response_rel),
                "completion_quality": float(completion_qual)
            }

            metadata.update({
                "query": query,
                "context": context,
                "response": response
            })

            metrics["metadata"] = metadata
            st.session_state.metrics_history.append(metrics)

    def get_metrics(self) -> Dict:
        """Get evaluation metrics"""
        if not st.session_state.metrics_history:
            return {
                "context_relevance": 0.0,
                "response_relevance": 0.0,
                "completion_quality": 0.0
            }

        df = pd.DataFrame([
            {k: v for k, v in m.items() if k != 'metadata'}
            for m in st.session_state.metrics_history
        ])

        return {
            "context_relevance": float(df["context_relevance"].mean()),
            "response_relevance": float(df["response_relevance"].mean()),
            "completion_quality": float(df["completion_quality"].mean())
        }