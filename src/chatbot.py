import time
import streamlit as st
from typing import Dict, List, Tuple
from snowflake.cortex import Complete

from src.retriever import CortexSearchRetriever
from src.utils import get_snowpark_session


class PolicyChatbot:
    def __init__(self):
        self.retriever = CortexSearchRetriever()

    def get_response(self, query: str) -> Tuple[str, List[Dict[str, str]]]:
        """
        Main method to get response for a query.
        Returns both response and reference information including sources
        """
        start_time = time.time()
        retrieval_start = time.time()

        # Get context with source information
        context_info = self.retriever.retrieve(query)
        retrieval_time = (time.time() - retrieval_start) * 1000

        # Generate response
        if not context_info:
            response = "I'm sorry, but I couldn't find relevant information to answer your question."
            return response, []

        # Extract just the text chunks for the prompt
        context_texts = [info['chunk'] for info in context_info]

        prompt = f"""
        You are a helpful government policy assistant. Using only the provided context, 
        answer questions about government policies and benefits.

        Context: {' '.join(context_texts)}

        Question: {query}

        Provide a clear, concise answer based only on the context provided. 
        If you're unsure or the information isn't in the context, say so.

        Response should be formatted in markdown for better readability.
        """

        try:
            response = Complete("mistral-large2", prompt, session=get_snowpark_session())
            return response, context_info

        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return "I apologize, but I'm having trouble generating a response right now.", []