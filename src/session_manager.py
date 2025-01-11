import streamlit as st
from snowflake.snowpark import Session


def get_snowflake_session():
    # Check if the session already exists in session state
    if "snowflake_session" not in st.session_state:
        print("Creating Snowflake session")
        connection_parameters = {
            "account": st.secrets["snowflake"]["account"],
            "user": st.secrets["snowflake"]["user"],
            "password": st.secrets["snowflake"]["password"],
            "warehouse": st.secrets["snowflake"]["warehouse"],
            "database": st.secrets["snowflake"]["database"],
            "schema": st.secrets["snowflake"]["schema"],
        }
        st.session_state.snowflake_session = Session.builder.configs(
            connection_parameters
        ).create()
    else:
        print("Using existing Snowflake session")
    return st.session_state.snowflake_session
