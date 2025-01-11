import time
import streamlit as st
from typing import Dict, List
import pandas as pd
from snowflake.cortex import Complete

from src.retriever import CortexSearchRetriever
from src.evaluator.trulens_evaluator import TruLensEvaluator
from src.evaluator.metrics import EnhancedMetrics
from src.evaluator.model_evaluator import ModelEvaluator

class PolicyChatbot:
    def __init__(self):
        self.retriever = CortexSearchRetriever()
        self.evaluator = TruLensEvaluator()
        self.metrics = EnhancedMetrics()

    @property
    def model_evaluator(self):
        if not hasattr(self, '_model_evaluator'):
            self._model_evaluator = ModelEvaluator()
        return self._model_evaluator

    def count_tokens(self, text: str) -> int:
        """Simple token count estimation"""
        return len(text.split())

    def get_response(self, query: str) -> str:
        """Main method to get response for a query"""
        start_time = time.time()
        retrieval_start = time.time()

        # Get context
        context = self.retriever.retrieve(query)
        retrieval_time = (time.time() - retrieval_start) * 1000

        # Generate response
        if not context:
            response = "I'm sorry, but I couldn't find relevant information to answer your question."
            end_time = time.time()
            total_latency = (end_time - start_time) * 1000

            # Track minimal metrics for failed queries
            self.metrics.track_interaction(
                prompt_tokens=self.count_tokens(query),
                completion_tokens=self.count_tokens(response),
                latency_ms=total_latency,
                cost=0.0
            )

            return response

        prompt = f"""
        You are a helpful government policy assistant. Using only the provided context, 
        answer questions about government policies and benefits.

        Context: {' '.join(context)}

        Question: {query}

        Provide a clear, concise answer based only on the context provided. 
        If you're unsure or the information isn't in the context, say so.
        """

        try:
            response = Complete("mistral-large2", prompt)
            end_time = time.time()

            # Calculate detailed metrics
            prompt_tokens = self.count_tokens(prompt)
            completion_tokens = self.count_tokens(response)
            total_latency = (end_time - start_time) * 1000

            # Cost calculation (based on Mistral's pricing)
            prompt_cost = (prompt_tokens / 1000) * 0.7  # $0.7 per 1K tokens for input
            completion_cost = (completion_tokens / 1000) * 2.0  # $2.0 per 1K tokens for output
            total_cost = prompt_cost + completion_cost

            # Track metrics
            self.metrics.track_interaction(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                latency_ms=total_latency,
                cost=total_cost
            )

            # Log feedback
            self.evaluator.log_feedback(
                query=query,
                context=context,
                response=response,
                metadata={
                    "timestamp": pd.Timestamp.now().isoformat(),
                    "latency_ms": total_latency,
                    "total_tokens": prompt_tokens + completion_tokens,
                    "cost": total_cost
                }
            )

            return response

        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return "I apologize, but I'm having trouble generating a response right now."

    def get_metrics(self) -> Dict:
        """Get current evaluation metrics"""
        return self.evaluator.get_metrics()