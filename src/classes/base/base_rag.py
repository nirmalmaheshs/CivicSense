from abc import ABC, abstractmethod
from typing import List


class BaseRag(ABC):

    @abstractmethod
    def retrieve_context(self, query: str) -> list:
        pass

    @abstractmethod
    def generate_completion(self, query: str, context: list, model_name: str) -> str:
        pass

    @abstractmethod
    def generate_standalone_question(
        self, query: str, history: list, model_name: str
    ) -> str:
        pass

    @abstractmethod
    def query(self, query: str, history: list) -> str:
        pass
