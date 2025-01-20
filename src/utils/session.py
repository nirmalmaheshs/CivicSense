import os
from dotenv import load_dotenv
from snowflake.snowpark.session import Session
from trulens.connectors.snowflake import SnowflakeConnector
from trulens.core import TruSession
import snowflake.connector


class AppSession:
    def __init__(self):
        load_dotenv()

        connection_params = {
            "account": os.getenv("SNOWFLAKE_ACCOUNT"),
            "user": os.getenv("SNOWFLAKE_USER"),
            "password": os.getenv("SNOWFLAKE_USER_PASSWORD"),
            "role": os.getenv("SNOWFLAKE_ROLE"),
            "database": os.getenv("SNOWFLAKE_DATABASE"),
            "schema": os.getenv("SNOWFLAKE_SCHEMA"),
            "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        }

        self.snowpark_session = Session.builder.configs(connection_params).create()
        self.tru_snowflake_connector = SnowflakeConnector(
            snowpark_session=self.snowpark_session
        )
        self.tru_session = TruSession(connector=self.tru_snowflake_connector)
        self.snowflake_connector = snowflake.connector.connect(**connection_params)


session = AppSession()
