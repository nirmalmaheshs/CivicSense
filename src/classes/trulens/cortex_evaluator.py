from src.classes.base.base_evaluator import BaseEvaluator
from trulens.providers.cortex.provider import Cortex
from trulens.core import Feedback, Select
from trulens.apps.custom import TruCustomApp, instrument
import numpy as np
from typing import Any
from src.utils.session import session
from src.classes.base.base_rag import BaseRag

class CortextEvaluator(BaseEvaluator):

    def get_groundedness_feedback(self) -> Any:
        return (
            Feedback(
                self.get_feedback_provider().groundedness_measure_with_cot_reasons,
                name="Groundedness",
            )
            .on(Select.RecordCalls.retrieve_context.rets[:].collect())
            .on_output()
        )

    def get_context_relevance(self) -> Any:
        return (
            Feedback(
                self.get_feedback_provider().context_relevance, name="Context Relevance"
            )
            .on_input()
            .on(Select.RecordCalls.retrieve_context.rets[:])
            .aggregate(np.mean)
        )

    def get_answer_relevance(self) -> Any:
        return (
            Feedback(self.get_feedback_provider().relevance, name="Answer Relevance")
            .on_input()
            .on_output()
            .aggregate(np.mean)
        )

    def get_cost_feedback(self) -> Any:
        return Feedback(
            self.get_feedback_provider().cost_estimate,
            name="Cost"
        ).on_output()

    def get_feedback_provider(self) -> Any:
        return Cortex(session.snowpark_session)

    def get_evaluator(self, rag: BaseRag, app_name: str, app_version: str) -> Any:
        instrument.method(BaseRag, BaseRag.generate_completion.__name__)
        instrument.method(BaseRag, BaseRag.query.__name__)
        instrument.method(BaseRag, BaseRag.retrieve_context.__name__)

        return TruCustomApp(
            app=rag,
            app_name=app_name,
            app_version=app_version,
            feedbacks=[
                self.get_groundedness_feedback(),
                self.get_answer_relevance(),
                self.get_context_relevance()
            ]
        )
