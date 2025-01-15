import pandas as pd
from src.utils.session import session


def get_feedback_metrics():
    query = """
        SELECT 
            f.name as NAME,
            min(f.result) as MIN_SCORE,
            avg(f.result) as AVG_SCORE,
            max(f.result) as MAX_SCORE,
            count(*) as QUERY_COUNT,
            a.APP_VERSION
        FROM TRULENS_FEEDBACKS f
        JOIN TRULENS_RECORDS r ON f.RECORD_ID = r.RECORD_ID
        JOIN TEST.PUBLIC.TRULENS_APPS a ON r.APP_ID = a.APP_ID
        GROUP BY f.name, a.APP_VERSION
        ORDER BY a.APP_VERSION DESC
    """
    return pd.read_sql(query, session.snowflake_connector)


def get_cost_metrics():
    query = """
        SELECT 
            DATE_TRUNC('hour', TO_TIMESTAMP_NTZ(r.TS::int)) as TIME,
            a.APP_VERSION,
            COUNT(*) as QUERY_COUNT,
            SUM(PARSE_JSON(r.COST_JSON):n_tokens::number) as TOKENS,
            SUM(PARSE_JSON(r.COST_JSON):n_prompt_tokens::number) as PROMPT_TOKENS,
            SUM(PARSE_JSON(r.COST_JSON):n_completion_tokens::number) as COMPLETION_TOKENS,
            SUM(PARSE_JSON(r.COST_JSON):cost::number) as COST,
            MAX(PARSE_JSON(r.COST_JSON):cost_currency::string) as CURRENCY
        FROM TRULENS_RECORDS r
        JOIN TEST.PUBLIC.TRULENS_APPS a ON r.APP_ID = a.APP_ID
        WHERE r.COST_JSON IS NOT NULL
            AND PARSE_JSON(r.COST_JSON):cost IS NOT NULL
        GROUP BY DATE_TRUNC('hour', TO_TIMESTAMP_NTZ(r.TS::int)), a.APP_VERSION
        ORDER BY TIME DESC, a.APP_VERSION DESC
    """
    return pd.read_sql(query, session.snowflake_connector)


def get_latency_metrics():
    query = """
        SELECT 
            DATE_TRUNC('hour', TO_TIMESTAMP_NTZ(r.TS::int)) as time,
            a.APP_VERSION,
            MIN(
                TIMESTAMPDIFF(
                    'MILLISECOND',
                    TO_TIMESTAMP(PARSE_JSON(r.RECORD_JSON):perf:start_time::string),
                    TO_TIMESTAMP(PARSE_JSON(r.RECORD_JSON):perf:end_time::string)
                ) / 1000.0
            ) as min_latency,
            AVG(
                TIMESTAMPDIFF(
                    'MILLISECOND',
                    TO_TIMESTAMP(PARSE_JSON(r.RECORD_JSON):perf:start_time::string),
                    TO_TIMESTAMP(PARSE_JSON(r.RECORD_JSON):perf:end_time::string)
                ) / 1000.0
            ) as avg_latency,
            MAX(
                TIMESTAMPDIFF(
                    'MILLISECOND',
                    TO_TIMESTAMP(PARSE_JSON(r.RECORD_JSON):perf:start_time::string),
                    TO_TIMESTAMP(PARSE_JSON(r.RECORD_JSON):perf:end_time::string)
                ) / 1000.0
            ) as max_latency,
            COUNT(*) as request_count
        FROM TRULENS_RECORDS r
        JOIN TEST.PUBLIC.TRULENS_APPS a ON r.APP_ID = a.APP_ID
        GROUP BY DATE_TRUNC('hour', TO_TIMESTAMP_NTZ(r.TS::int)), a.APP_VERSION
        ORDER BY time DESC, a.APP_VERSION DESC
    """
    return pd.read_sql(query, session.snowflake_connector)


def get_daily_stats():
    query = """
        SELECT 
            DATE_TRUNC('day', TO_TIMESTAMP_NTZ(r.TS::int)) as day,
            a.APP_VERSION,
            COUNT(*) as query_count,
            AVG(
                TIMESTAMPDIFF(
                    'MILLISECOND',
                    TO_TIMESTAMP(PARSE_JSON(r.RECORD_JSON):perf:start_time::string),
                    TO_TIMESTAMP(PARSE_JSON(r.RECORD_JSON):perf:end_time::string)
                ) / 1000.0
            ) as avg_latency,
            COUNT(DISTINCT r.APP_ID) as version_count,
            AVG(PARSE_JSON(r.COST_JSON):cost::float) as avg_cost
        FROM TRULENS_RECORDS r
        JOIN TEST.PUBLIC.TRULENS_APPS a ON r.APP_ID = a.APP_ID
        GROUP BY DATE_TRUNC('day', TO_TIMESTAMP_NTZ(r.TS::int)), a.APP_VERSION
        ORDER BY day DESC, a.APP_VERSION DESC
        LIMIT 7
    """
    return pd.read_sql(query, session.snowflake_connector)


def get_model_evaluation_metrics():
    """Get metrics for model configuration comparison"""
    query = """
        SELECT 
            r.APP_ID,
            a.APP_NAME,
            a.APP_VERSION,
            COUNT(*) as total_queries,
            AVG(CASE WHEN f.name = 'Groundedness' THEN f.result END) as avg_groundedness,
            AVG(CASE WHEN f.name = 'Context Relevance' THEN f.result END) as avg_context_relevance,
            AVG(CASE WHEN f.name = 'Answer Relevance' THEN f.result END) as avg_answer_relevance,
            AVG(
                TIMESTAMPDIFF(
                    'MILLISECOND',
                    TO_TIMESTAMP(PARSE_JSON(r.RECORD_JSON):perf:start_time::string),
                    TO_TIMESTAMP(PARSE_JSON(r.RECORD_JSON):perf:end_time::string)
                ) / 1000.0
            ) as avg_latency,
            AVG(PARSE_JSON(r.COST_JSON):cost::float) as avg_cost
        FROM TRULENS_RECORDS r
        LEFT JOIN TRULENS_FEEDBACKS f ON r.RECORD_ID = f.RECORD_ID
        JOIN TEST.PUBLIC.TRULENS_APPS a ON r.APP_ID = a.APP_ID
        GROUP BY r.APP_ID, a.APP_NAME, a.APP_VERSION
        ORDER BY a.APP_VERSION DESC
    """
    return pd.read_sql(query, session.snowflake_connector)


def get_configuration_details():
    """Get configuration details from TAGS and TRULENS_APPS"""
    query = """
        SELECT DISTINCT
            r.APP_ID,
            a.APP_NAME,
            a.APP_VERSION,
            r.TAGS,
            PARSE_JSON(a.APP_JSON):metadata as CONFIG_DETAILS
        FROM TRULENS_RECORDS r
        JOIN TEST.PUBLIC.TRULENS_APPS a ON r.APP_ID = a.APP_ID
        WHERE r.TAGS != '[]'
        ORDER BY a.APP_VERSION DESC
    """
    return pd.read_sql(query, session.snowflake_connector)