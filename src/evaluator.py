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
        session = get_snowpark_session()

        # Initialize Snowflake connector and TruSession
        sf_connector = SnowflakeConnector(
            snowpark_session=session
        )
        self.session = TruSession(connector=sf_connector)

        # Initialize feedback provider
        self.provider = Cortex(snowpark_session=session)

        # Define feedback functions
        feedbacks = [
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

        # Initialize TruLens app
        if "chatbot" in st.session_state:
            self.tru_app = TruCustomApp(
                st.session_state.chatbot,
                app_name="PolicyBot",
                feedbacks=feedbacks
            )