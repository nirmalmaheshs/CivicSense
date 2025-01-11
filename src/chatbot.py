from typing import Dict, List

import numpy as np
import streamlit as st
from snowflake.cortex import Complete
from trulens.providers.cortex.provider import Cortex
from trulens.core import Feedback, Select
from trulens.apps.custom import instrument, TruCustomApp

from src.retriever import CortexSearchRetriever
from snowflake.snowpark.context import get_active_session
from src.utils import get_tru_lens_session


class PolicyChatbot:
    def __init__(self):
        self.retriever = CortexSearchRetriever()

        # Get Snowflake session and set default
        session = get_active_session()
        Cortex.DEFAULT_SNOWPARK_SESSION = session

        # Initialize TruLens instrumentation
        self.tru_recorder = TruCustomApp(
            self,
            app_name="PolicyChatbot",
            feedbacks=self._initialize_feedback(session)
        )

    def _initialize_feedback(self, session) -> List[Feedback]:
        """Initialize TruLens feedback functions"""
        provider = Cortex(
            model_id="mistral-large2"
        )

        f_groundedness = (
            Feedback(provider.groundedness_measure_with_cot_reasons, name="Groundedness")
            .on(Select.RecordCalls.retrieve_context.rets[:].collect())
            .on_output()
        )

        f_context_relevance = (
            Feedback(provider.context_relevance, name="Context Relevance")
            .on_input()
            .on(Select.RecordCalls.retrieve_context.rets[:])
            .aggregate(np.mean)
        )

        # Answer relevance feedback
        f_answer_relevance = (
            Feedback(provider.relevance, name="Answer Relevance")
            .on_input()
            .on_output()
            .aggregate(np.mean)
        )

        return [f_groundedness, f_context_relevance, f_answer_relevance]

    @instrument
    def retrieve_context(self, query: str) -> List[str]:
        """Get context from retriever"""
        return self.retriever.retrieve(query)

    @instrument
    def get_response(self, query: str) -> str:
        """Main method to get response for a query"""
        try:
            # Get context
            context = self.retrieve_context(query)

            if not context:
                return "I'm sorry, but I couldn't find relevant information to answer your question."

            prompt = f"""
            You are a helpful government policy assistant. Using only the provided context, 
            answer questions about government policies and benefits.

            Context: {' '.join(context)}

            Question: {query}

            Provide a clear, concise answer based only on the context provided. 
            If you're unsure or the information isn't in the context, say so.
            """

            response = Complete("mistral-large2", prompt)
            return response

        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return "I apologize, but I'm having trouble generating a response right now."

    def get_metrics(self) -> Dict:
        """Get evaluation metrics from TruLens"""
        from trulens.core import TruSession
        from trulens.connectors.snowflake import SnowflakeConnector

        tru = get_tru_lens_session()

        # Get leaderboard
        leaderboard = tru.get_leaderboard()

        if leaderboard.empty:
            return {
                "groundedness": 0.0,
                "context_relevance": 0.0,
                "answer_relevance": 0.0
            }

        return {
            "groundedness": leaderboard["Groundedness"].mean(),
            "context_relevance": leaderboard["Context Relevance"].mean(),
            "answer_relevance": leaderboard["Answer Relevance"].mean()
        }