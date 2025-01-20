from abc import ABC, abstractmethod
from typing import List


class BaseRag(ABC):

    @abstractmethod
    def retrieve_context(self, query: str) -> list:
        pass

    @abstractmethod
    def generate_completion(self, query: str, context: list) -> str:
        pass

    @abstractmethod
    def query(self, query: str) -> str:
        pass
