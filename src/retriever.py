from typing import List, Dict
import streamlit as st
from snowflake.core import Root
from src.utils import get_snowpark_session

class CortexSearchRetriever:
    def __init__(self, limit_to_retrieve: int = 4):
        self.limit_to_retrieve = limit_to_retrieve
        self.session = get_snowpark_session()

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

                    results.append({
                        'chunk': curr["chunk"],
                        'source': relative_path,
                        'signed_url': signed_url
                    })
                return results

        except Exception as e:
            st.error(f"Error in retrieval: {str(e)}")
        return []