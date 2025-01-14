import numpy as np
import streamlit as st
from trulens.core import Select, TruSession, Feedback
from trulens.providers.cortex.provider import Cortex
from trulens.apps.custom import TruCustomApp
from trulens.connectors.snowflake import SnowflakeConnector
from src.utils import get_snowpark_session


class Evaluator:
    def __init__(self):
        # Get Snowflake session
        self.snowpark_session = get_snowpark_session()

        # Initialize Snowflake connector
        self.sf_connector = SnowflakeConnector(
            snowpark_session=self.snowpark_session
        )

        # Initialize TruSession
        self.session = TruSession(connector=self.sf_connector)

        # Initialize feedback provider
        self.provider = Cortex(snowpark_session=self.snowpark_session)

        # Define feedback functions
        self.feedbacks = [
            Feedback(
                self.provider.groundedness_measure_with_cot_reasons,
                name="Groundedness"
            ).on(Select.RecordCalls.retrieve.rets).on_output(),

            Feedback(
                self.provider.relevance_with_cot_reasons,
                name="Answer Relevance"
            ).on_input().on_output(),

            Feedback(
                self.provider.context_relevance_with_cot_reasons,
                name="Context Relevance"
            ).on_input().on(Select.RecordCalls.retrieve.rets).aggregate(np.mean)
        ]

        # Initialize TruLens app with retries
        if "chatbot" in st.session_state:
            max_retries = 3
            last_error = None
            for attempt in range(max_retries):
                try:
                    self.tru_app = TruCustomApp(
                        st.session_state.chatbot,
                        app_name="PolicyBot",
                        feedbacks=self.feedbacks
                    )
                    break
                except Exception as e:
                    last_error = e
                    if attempt == max_retries - 1:
                        st.error(f"Failed to initialize TruLens app: {str(last_error)}")
                        raise e
                    else:
                        import time
                        time.sleep(1)

    def get_leaderboard(self):
        """Get the evaluation leaderboard with error handling"""
        try:
            leaderboard = self.session.get_leaderboard()
            if leaderboard is None or leaderboard.empty:
                print("No metrics available yet")
                return None
            return leaderboard
        except Exception as e:
            print(f"Error getting leaderboard: {str(e)}")
            return None