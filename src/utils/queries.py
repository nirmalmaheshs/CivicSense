import pandas as pd
from src.utils.session import session


def get_feedback_metrics():
    query = """
        select 
            name as NAME,
            min(result) as MIN_SCORE,
            avg(result) as AVG_SCORE,
            max(result) as MAX_SCORE,
            count(*) as QUERY_COUNT
        from TRULENS_FEEDBACKS
        group by name
    """
    return pd.read_sql(query, session.snowflake_connector)


def get_cost_metrics():
    query = """
        SELECT 
            DATE_TRUNC('hour', TO_TIMESTAMP_NTZ(TS::int)) as TIME,
            COUNT(*) as QUERY_COUNT,
            SUM(PARSE_JSON(COST_JSON):n_tokens::number) as TOKENS,
            SUM(PARSE_JSON(COST_JSON):n_prompt_tokens::number) as PROMPT_TOKENS,
            SUM(PARSE_JSON(COST_JSON):n_completion_tokens::number) as COMPLETION_TOKENS,
            SUM(PARSE_JSON(COST_JSON):cost::number) as COST,
            MAX(PARSE_JSON(COST_JSON):cost_currency::string) as CURRENCY
        FROM TRULENS_RECORDS
        WHERE COST_JSON IS NOT NULL
            AND PARSE_JSON(COST_JSON):cost IS NOT NULL
        GROUP BY DATE_TRUNC('hour', TO_TIMESTAMP_NTZ(TS::int))
        ORDER BY TIME
    """
    return pd.read_sql(query, session.snowflake_connector)


def get_latency_metrics():
    query = """
        SELECT 
    DATE_TRUNC('hour', TO_TIMESTAMP_NTZ(TS::int)) as time,
    MIN(
        TIMESTAMPDIFF(
            'MILLISECOND',
            TO_TIMESTAMP(PARSE_JSON(RECORD_JSON):perf:start_time::string),
            TO_TIMESTAMP(PARSE_JSON(RECORD_JSON):perf:end_time::string)
        ) / 1000.0
    ) as min_latency,
    AVG(
        TIMESTAMPDIFF(
            'MILLISECOND',
            TO_TIMESTAMP(PARSE_JSON(RECORD_JSON):perf:start_time::string),
            TO_TIMESTAMP(PARSE_JSON(RECORD_JSON):perf:end_time::string)
        ) / 1000.0
    ) as avg_latency,
    MAX(
        TIMESTAMPDIFF(
            'MILLISECOND',
            TO_TIMESTAMP(PARSE_JSON(RECORD_JSON):perf:start_time::string),
            TO_TIMESTAMP(PARSE_JSON(RECORD_JSON):perf:end_time::string)
        ) / 1000.0
    ) as max_latency,
    COUNT(*) as request_count
FROM TRULENS_RECORDS
GROUP BY DATE_TRUNC('hour', TO_TIMESTAMP_NTZ(TS::int))
ORDER BY time
    """
    return pd.read_sql(query, session.snowflake_connector)

def get_daily_stats():
    query = """
        select 
    DATE_TRUNC('day', TO_TIMESTAMP_NTZ(TS::int)) as day,
    COUNT(*) as query_count,
    AVG(
        TIMESTAMPDIFF(
            'MILLISECOND',
            TO_TIMESTAMP(PARSE_JSON(RECORD_JSON):perf:start_time::string),
            TO_TIMESTAMP(PARSE_JSON(RECORD_JSON):perf:end_time::string)
        ) / 1000.0
    ) as avg_latency,
    COUNT(DISTINCT APP_ID) as version_count,
    AVG(PARSE_JSON(COST_JSON):cost::float) as avg_cost
from TRULENS_RECORDS
group by DATE_TRUNC('day', TO_TIMESTAMP_NTZ(TS::int))
order by day desc
limit 7
    """
    return pd.read_sql(query, session.snowflake_connector)

# Add to queries.py
def get_model_evaluation_metrics():
    """Get metrics for model configuration comparison"""
    query = """
    SELECT 
        r.APP_ID,
        COUNT(*) as total_queries,
        AVG(CASE WHEN name = 'Groundedness' THEN result END) as avg_groundedness,
        AVG(CASE WHEN name = 'Context Relevance' THEN result END) as avg_context_relevance,
        AVG(CASE WHEN name = 'Answer Relevance' THEN result END) as avg_answer_relevance,
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
    GROUP BY r.APP_ID
    ORDER BY r.APP_ID
    """
    return pd.read_sql(query, session.snowflake_connector)

def get_configuration_details():
    """Get configuration details from TAGS"""
    query = """
    SELECT DISTINCT
        APP_ID,
        TAGS
    FROM TRULENS_RECORDS
    WHERE TAGS != '[]'
    ORDER BY APP_ID
    """
    return pd.read_sql(query, session.snowflake_connector)