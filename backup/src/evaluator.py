import numpy as np
import streamlit as st
from trulens.core import Feedback
from trulens.core import Select
from trulens.providers.cortex import Cortex
from src.utils import get_snowpark_session
from trulens.apps.custom import TruCustomApp
from trulens.core import TruSession


class Evaluator:

    def __init__(self):
        provider = Cortex(snowpark_session=get_snowpark_session())

        # Define a groundedness feedback function
        f_groundedness = (
            Feedback(
                provider.groundedness_measure_with_cot_reasons, name="Groundedness"
            )
            .on(Select.RecordCalls.retrieve.rets.collect())
            .on_output()
        )
        # Question/answer relevance between overall question and answer.
        f_answer_relevance = (
            Feedback(provider.relevance_with_cot_reasons, name="Answer Relevance")
            .on_input()
            .on_output()
        )

        # Context relevance between question and each context chunk.
        f_context_relevance = (
            Feedback(
                provider.context_relevance_with_cot_reasons, name="Context Relevance"
            )
            .on_input()
            .on(Select.RecordCalls.retrieve.rets[:])
            .aggregate(np.mean)
        )

        rag = st.session_state.chatbot

        self.session = TruSession()

        self.tru_app = TruCustomApp(
            rag,
            app_name="RAG",
            app_version="base",
            feedbacks=[f_groundedness, f_answer_relevance, f_context_relevance],
        )
