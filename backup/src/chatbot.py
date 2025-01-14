import streamlit as st
from typing import Dict, List, Tuple
from snowflake.cortex import Complete
from src.utils import get_snowpark_session
from trulens.apps.custom import instrument
from snowflake.core import Root


class PolicyChatbot:

    def __init__(self, limit_to_retrieve: int = 4):
        self.limit_to_retrieve = limit_to_retrieve
        self.session = get_snowpark_session()

    @instrument
    def query(self, query: str) -> str:
        context_info = self.retrieve(query)
        return self.get_response(query, context_info)

    @instrument
    def get_response(
        self, query: str, context_info: list
    ) -> Tuple[str, List[Dict[str, str]]]:
        """
        Main method to get response for a query.
        Returns both response and reference information including sources
        """

        # Generate response
        if not context_info:
            response = "I'm sorry, but I couldn't find relevant information to answer your question."
            return response, []

        # Extract just the text chunks for the prompt
        context_texts = [info["chunk"] for info in context_info]

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
            response = Complete("mistral-large2", prompt, session=self.session)
            return response, context_info

        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return (
                "I apologize, but I'm having trouble generating a response right now.",
                [],
            )

    def _generate_signed_url(self, relative_path: str) -> str:
        """Generate a signed URL for a given file path"""
        try:
            stage_location = "@docs"  # Replace with your stage name
            sql = f"SELECT GET_PRESIGNED_URL({stage_location}, '{relative_path}')"
            result = self.session.sql(sql).collect()
            if result:
                return result[0][0]
        except Exception as e:
            st.error(f"Error generating signed URL: {str(e)}")
        return ""

    @instrument
    def retrieve(self, query: str) -> List[Dict[str, str]]:
        """
        Retrieve relevant chunks with their source information and generate signed URLs
        """
        root = Root(self.session)
        try:
            cortex_search_service = (
                root.databases[st.secrets["snowflake"]["database"]]
                .schemas[st.secrets["snowflake"]["schema"]]
                .cortex_search_services["CC_SEARCH_SERVICE_CS"]
            )

            # Get the search results
            resp = cortex_search_service.search(
                query=query,
                columns=["chunk", "relative_path"],  # Only request available columns
                limit=self.limit_to_retrieve,
            )

            if resp.results:
                results = []
                for curr in resp.results:
                    relative_path = curr.get("relative_path", "")
                    signed_url = ""
                    if relative_path:
                        signed_url = self._generate_signed_url(relative_path)

                    results.append(
                        {
                            "chunk": curr["chunk"],
                            "source": relative_path,
                            "signed_url": signed_url,
                        }
                    )
                return results

        except Exception as e:
            st.error(f"Error in retrieval: {str(e)}")
        return []
