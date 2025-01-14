from src.classes.base.base_rag import BaseRag
from src.classes.snowflake.cortex_search_retriever import CortexSearchRetriever
from src.utils.session import session
from snowflake.cortex import complete
from trulens.apps.custom import instrument

class Predictor(BaseRag):

    def __init__(self):
        self.retriever = CortexSearchRetriever(
            snowpark_session=session.snowpark_session, limit_to_retrieve=4
        )

    @instrument
    def retrieve_context(self, query: str) -> list:
        """
        Retrieve relevant text from vector store.
        """
        return self.retriever.retrieve(query)

    @instrument
    def generate_completion(self, query: str, context_str: list) -> str:
        """
        Generate answer from context.
        """
        prompt = f"""
          You are an expert assistant extracting information from context provided.
          Answer the question based on the context. Be concise and do not hallucinate.
          If you don´t have the information just say so.
          Context: {context_str}
          Question:
          {query}
          Answer:
        """
        return complete("mistral-large", prompt, session=session.snowpark_session)

    @instrument
    def query(self, query: str) -> str:
        context_str = self.retrieve_context(query)
        return self.generate_completion(query, context_str)
