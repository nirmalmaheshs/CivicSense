import pandas as pd
from src.utils.session import session


def get_feedback_metrics():
    query = """
        select name,
        min(result) as min_feedback_relevance,
        avg(result) as avg_feedback_relevance,
        max(result) as max_feedback_relevance
        from TRULENS_FEEDBACKS
        group by name
    """
    return pd.read_sql(query, session.snowflake_connector)


def get_cost_metrics():
    query = """
        select json_object:cost as cost, json_object:n_tokens as tokens
        from(
        select PARSE_JSON(cost_json) AS json_object
        from TRULENS_RECORDS)
    """
    return pd.read_sql(query, session.snowflake_connector)


def get_latency_metrics():
    query = """
        select TS as latency from TRULENS_RECORDS
    """
    return pd.read_sql(query, session.snowflake_connector)
