import streamlit as st
from snowflake.snowpark import Session


def get_snowpark_session():
    """Get or create Snowflake session using singleton pattern"""
    if "snowpark_session" not in st.session_state:
        try:
            # Connection parameters from Streamlit secrets
            connection_parameters = {
                "account": st.secrets["snowflake"]["account"],
                "user": st.secrets["snowflake"]["user"],
                "password": st.secrets["snowflake"]["password"],
                "warehouse": st.secrets["snowflake"]["warehouse"],
                "database": st.secrets["snowflake"]["database"],
                "schema": st.secrets["snowflake"]["schema"],
                "client_session_keep_alive": True,  # Keep session alive
            }

            # Create session with configurations
            session = Session.builder.configs(connection_parameters).create()

            # Store in session state
            st.session_state.snowpark_session = session

        except Exception as e:
            st.error(f"Failed to create Snowflake session: {str(e)}")
            raise e

    return st.session_state.snowpark_session

