import os
from snowflake.core import Root
from snowflake.snowpark.session import Session
from typing import List
from src.classes.base.base_retriever import BaseRetriever


class CortexSearchRetriever(BaseRetriever):

    def __init__(self, snowpark_session: Session, limit_to_retrieve: int = 4):
        self._snowpark_session = snowpark_session
        self._limit_to_retrieve = limit_to_retrieve

    def retrieve(self, query: str) -> List[dict]:
        root = Root(self._snowpark_session)
        cortex_search_service = (
            root.databases[os.getenv("SNOWFLAKE_DATABASE")]
            .schemas[os.getenv("SNOWFLAKE_SCHEMA")]
            .cortex_search_services[os.getenv("SNOWFLAKE_CORTEX_SEARCH_SERVICE")]
        )

        resp = cortex_search_service.search(
            query=query,
            columns=["chunk", "relative_path"],
            limit=self._limit_to_retrieve,
        )

        if resp.results:
            return [{
                "chunk": curr["chunk"],
                "relative_path": curr["relative_path"]
            } for curr in resp.results]
        else:
            return []
