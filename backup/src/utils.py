import streamlit as st
from snowflake.snowpark import Session

def get_snowpark_session():
    """Get or create Snowflake session using singleton pattern"""
    if "snowpark_session" not in st.session_state:
        connection_parameters = {
            "account": st.secrets["snowflake"]["account"],
            "user": st.secrets["snowflake"]["user"],
            "password": st.secrets["snowflake"]["password"],
            "warehouse": st.secrets["snowflake"]["warehouse"],
            "database": st.secrets["snowflake"]["database"],
            "schema": st.secrets["snowflake"]["schema"],
        }
        session = Session.builder.configs(connection_parameters).create()
        st.session_state.snowpark_session = session
    return st.session_state.snowpark_session

