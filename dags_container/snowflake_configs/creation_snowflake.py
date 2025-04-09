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
    use_existing()
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
        CREATE FILE FORMAT IF NOT EXISTS {FILE_FORMAT_NAME}
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
    
  
def create_base_tables():
    use_existing()

    create_table_restaurant = """
        CREATE TABLE IF NOT EXISTS restaurants (
            restaurant_id INT NOT NULL,
            restaurant_name VARCHAR(50),
            PRIMARY KEY(restaurant_id));
    """

    create_table_platform = """
        CREATE TABLE IF NOT EXISTS platforms (
            platform_id INT IDENTITY START 1 INCREMENT 1,
            platform_name VARCHAR(50),
            PRIMARY KEY(platform_id));
    """

    create_customer_table = """
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INT PRIMARY KEY IDENTITY START 1 INCREMENT 1,
            customer_name VARCHAR(100) NOT NULL,
            customer_phone VARCHAR(50) NOT NULL,
            customer_email VARCHAR(50) NOT NULL);
    """


    create_experience_table = """
        CREATE TABLE IF NOT EXISTS experiences (
            experience_id INT PRIMARY KEY IDENTITY START 1 INCREMENT 1,
            experience_name VARCHAR(50),
            price DECIMAL(10, 2))
    """

    create_table_payments = """
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INT PRIMARY KEY IDENTITY START 1 INCREMENT 1,
            payment_method VARCHAR(10) NOT NULL,
            card_last_four INT,
            amount_paid DECIMAL(10, 2) NOT NULL,
            tip_amount DECIMAL(10, 2),
            service_fee DECIMAL(10,2),
            total_amount DECIMAL(10, 2)
        )
    """

    create_table_reservation = """
        CREATE TABLE IF NOT EXISTS reservation (
            reservation_id VARCHAR(100) PRIMARY KEY,  
            restaurant_id INT REFERENCES restaurants(restaurant_id),
            platform INT REFERENCES platforms(platform_id),
            status VARCHAR(10) NOT NULL,
            reservation_date DATETIME NOT NULL,
            party_size INT NOT NULL,
            customer_id INT REFERENCES customers(customer_id),
            special_request TEXT, 
            created_at DATETIME, 
            updated_at DATETIME, 
            experience INT REFERENCES experiences(experience_id),
            payment INT REFERENCES payments(payment_id)
        
        )
       
    """
    try:
        curr.execute(create_table_restaurant)
        curr.execute(create_table_platform)
        curr.execute(create_customer_table)
        curr.execute(create_experience_table)
        curr.execute(create_table_payments)
        curr.execute(create_table_reservation)
    except Exception as e:
        logger.error(f"An error occured while creating the tables: {e}")

def insert_into_restaurant_platform_table():
    """
        One time load script
    """
    use_existing()
    try:
        insert_into_restaurant = """
            INSERT INTO restaurants(restaurant_id, restaurant_name) 
            SELECT DISTINCT $1:restaurant_id::INT, $1:restaurant_name
            FROM @S3_STAGE_TEST/2025-04-09
            (FILE_FORMAT => 'READ_RESERVATION_JSON')

        """

        insert_into_platform = """

            INSERT INTO platforms(platform_name)
            SELECT DISTINCT $1:platform
            FROM @s3_stage_test/2025-04-09
            (FILE_FORMAT => 'READ_RESERVATION_JSON')

        """

        curr.execute(insert_into_restaurant)
        curr.execute(insert_into_platform)
    except Exception as e:
        logger.error(f"An error occured while inserting data into restaurant/platform table...: {e}")