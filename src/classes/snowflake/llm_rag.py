from src.classes.base.base_rag import BaseRag
from src.classes.snowflake.cortex_search_retriever import CortexSearchRetriever
from src.utils.config import Defaults
from src.utils.session import session
from snowflake.cortex import complete


class Predictor(BaseRag):

    def __init__(self, chunk_size=Defaults.LLM_RETRIEVE_CHUNK_SIZE):
        self.retriever = CortexSearchRetriever(
            snowpark_session=session.snowpark_session, limit_to_retrieve=chunk_size
        )

    def retrieve_context(self, query: str) -> list:
        """
        Retrieve relevant text from vector store.
        """
        return self.retriever.retrieve(query)

    def generate_completion(
        self, query: str, context_str: list, model_name=Defaults.LLM_MODEL
    ) -> dict:
        """
        Generate answer from context with source references.
        Returns a dict containing the answer and sources.
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
        answer = complete(model_name, prompt, session=session.snowpark_session)

        # Extract source filenames from the context results
        sources = [
            source["relative_path"]
            for source in context_str
            if "relative_path" in source
        ]

        return {"answer": answer, "sources": sources}

    def generate_standalone_question(
        self, query: str, history: list, model_name=Defaults.LLM_MODEL
    ) -> str:
        prompt = f"""
            Given the following chat history and a user question,
            rephrase the follow up input question to be a standalone question.
            Chat History: {str(history)}
            User Question: {query}
            Standalone question:
        """
        return complete(model_name, prompt, session=session.snowpark_session)

    def query(self, query: str, history: list) -> dict:
        standalone_question = self.generate_standalone_question(query, history)
        print(f"Standalone Question: {standalone_question}")
        context_str = self.retrieve_context(standalone_question)
        return self.generate_completion(query, context_str)
