import streamlit as st
from snowflake.snowpark import Session

def get_snowpark_session():
    """Get or create Snowflake session using singleton pattern"""
    if 'snowpark_session' not in st.session_state:
        connection_parameters = {
            "account": st.secrets["snowflake"]["account"],
            "user": st.secrets["snowflake"]["user"],
            "password": st.secrets["snowflake"]["password"],
            "warehouse": st.secrets["snowflake"]["warehouse"],
            "database": st.secrets["snowflake"]["database"],
            "schema": st.secrets["snowflake"]["schema"]
        }
        session = Session.builder.configs(connection_parameters).create()
        st.session_state.snowpark_session = session
    return st.session_state.snowpark_session

def display_metrics(metrics: dict):
    """Display evaluation metrics in Streamlit"""
    st.sidebar.header("Evaluation Metrics")

    col1, col2, col3 = st.sidebar.columns(3)

    with col1:
        st.metric(
            "Context Relevance",
            f"{metrics.get('context_relevance', 0):.2f}",
            help="Measures how relevant the retrieved context is to the query"
        )

    with col2:
        st.metric(
            "Response Relevance",
            f"{metrics.get('response_relevance', 0):.2f}",
            help="Measures how relevant the response is to the query"
        )

    with col3:
        st.metric(
            "Completion Quality",
            f"{metrics.get('completion_quality', 0):.2f}",
            help="Measures the overall quality of the response"
        )

def initialize_app():
    """Initialize the application state"""
    # Initialize chatbot first
    if 'chatbot' not in st.session_state:
        from src.chatbot import PolicyChatbot
        st.session_state.chatbot = PolicyChatbot()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "debug_mode" not in st.session_state:
        st.session_state.debug_mode = False

    # Ensure evaluator is initialized
    if 'evaluation_results' not in st.session_state:
        st.session_state.evaluation_results = []

    if 'model_configurations' not in st.session_state:
        st.session_state.model_configurations = []

    return st.session_state.chatbot