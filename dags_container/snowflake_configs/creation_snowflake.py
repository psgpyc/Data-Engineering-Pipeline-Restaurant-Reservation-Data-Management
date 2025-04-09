import logging
from snowflake_configs.establish_connection import get_connector

curr = get_connector().cursor()

logger = logging.getLogger("custom_pipeline_logger")

def use_existing():
    curr.execute("USE ROLE accountadmin")
    curr.execute("USE DATABASE ozzy")
    curr.execute("USE SCHEMA base")


def create_database_and_schema():
    try:
        curr.execute("USE ROLE accountadmin")
        curr.execute("CREATE DATABASE IF NOT EXISTS ozzy")
        curr.execute("USE DATABASE ozzy")
        curr.execute("CREATE SCHEMA IF NOT EXISTS ozzy.base")
        curr.execute("USE SCHEMA base")
    except Exception as e:
        logger.error(f"Error occured when creating database and schema: {e}")
    finally:
        curr.close()


def create_external_stage():
    try:
        curr.execute("""
            CREATE OR REPLACE STAGE ozzy.base.s3_stage_test
            URL = 's3://booking-staging-bucket/'
            STORAGE_INTEGRATION = ozzy_pipeline_s3_access;
                    
                
        """)
        logger.info("Successfully created external stage")

    except Exception as e:
        logger.error(f"An error occured while creating and loading the stage: {e}")
    finally:
        curr.close()

def create_file_format():
    FILE_FORMAT_NAME = "read_reservation_json"

    use_existing()

    file_format_script = f"""
        CREATE FILE FORMAT  IF NOT EXISTS {FILE_FORMAT_NAME}
        TYPE = 'JSON'

        COMPRESSION = 'NONE'

        TRIM_SPACE = TRUE

        STRIP_OUTER_ARRAY = TRUE

        NULL_IF = ('', 'NULL')

        STRIP_NULL_VALUES = FALSE
    """

    try:
        curr.execute(file_format_script)
        logger.info("Successfully created Json file format")
    except Exception as e:
        logger.info(f"An error occured while creating a fileformat: {e}")
    
  
