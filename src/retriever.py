from typing import List
import streamlit as st
from snowflake.core import Root
from snowflake.snowpark.context import get_active_session


class CortexSearchRetriever:
    def __init__(self, limit_to_retrieve: int = 4):
        self.limit_to_retrieve = limit_to_retrieve

    def retrieve(self, query: str) -> List[str]:
        session = get_active_session()
        root = Root(session)
        try:
            cortex_search_service = (
                root.databases[st.secrets["snowflake"]["database"]]
                .schemas[st.secrets["snowflake"]["schema"]]
                .cortex_search_services["CC_SEARCH_SERVICE_CS"]
            )

            resp = cortex_search_service.search(
                query=query,
                columns=["chunk"],
                limit=self.limit_to_retrieve,
            )

            if resp.results:
                return [curr["chunk"] for curr in resp.results]
        except Exception as e:
            st.error(f"Error in retrieval: {str(e)}")
        return []