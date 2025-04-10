import os
import logging
from snowflake import connector
from dotenv import load_dotenv


load_dotenv()

logger = logging.getLogger('custom_pipeline_logger')


def get_connector(SNOWFLAKE_DATABASE = "OZZY", SNOWFLAKE_SCHEMA = "BASE"):
    
    conn_param = {
            "account": os.environ.get('snowflake_account'),
            "user": os.environ.get('snowflake_user'),
            "password": os.environ.get('snowflake_password'),
            "role": os.environ.get("snowflake_user_role"),
            "warehouse": os.environ.get('snowflake_warehouse'),
            "database": SNOWFLAKE_DATABASE,
            "schema": SNOWFLAKE_SCHEMA
        }
    
    try:
        conn = connector.connect(**conn_param)
    except Exception as e:
        logger.error(f'An error occured while connecting to snowflake: {e}')

    return conn


