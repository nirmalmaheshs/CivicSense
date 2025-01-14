from abc import ABC, abstractmethod
from typing import Any
from src.classes.base.base_rag import BaseRag


class BaseEvaluator(ABC):

    @abstractmethod
    def get_groundedness_feedback(self) -> Any:
        pass

    @abstractmethod
    def get_context_relevance(self) -> Any:
        pass

    @abstractmethod
    def get_answer_relevance(self) -> Any:
        pass

    @abstractmethod
    def get_feedback_provider(self) -> Any:
        pass

    @abstractmethod
    def get_evaluator(self, rag: BaseRag, app_name: str, app_version: str) -> Any:
        pass
