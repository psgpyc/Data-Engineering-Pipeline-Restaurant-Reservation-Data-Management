import logging
from datetime import datetime
from snowflake_configs.establish_connection import get_connector

conn = get_connector()

date_today = datetime.now().strftime("%Y-%m-%d")

logger = logging.getLogger("custom_pipeline_logger")

# def select_roles_schema(database_name, database_schema, role):
#     curr.execute(f"USE ROLE {database_name}")
#     curr.execute(f"USE DATABASE {database_schema}")
#     curr.execute(f"USE SCHEMA {role}")


def create_schema(database_name, database_schema, role="sysadmin"):
    try:
        with conn.cursor() as curr:
            curr.execute(f"USE ROLE {role}")
            curr.execute(f"USE DATABASE {database_name}")
            curr.execute(f"CREATE SCHEMA IF NOT EXISTS {database_name}.{database_schema}")
    except Exception as e:
        logger.error(f"Error occured when creating schema: {e}")
        raise RuntimeError(f"Failed to create schema {database_name}: {e}")


                  

def create_database(database_name, role="sysadmin"):
    try:
        with conn.cursor() as curr:
            curr.execute(f"USE ROLE {role}")
            curr.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
    except Exception as e:
        logger.error(f"Error occured when creating database and schema: {e}")
        raise RuntimeError(f"Failed to create database {database_name}: {e}")
   


def create_external_stage(stage_name, database_name, schema_name, storage_integration_name, bucket_url='s3://booking-staging-bucket/'):
    try:
        with conn.cursor() as curr:
            curr.execute(f"""
                CREATE OR REPLACE STAGE {database_name}.{schema_name}.{stage_name}
                URL = {bucket_url}
                STORAGE_INTEGRATION = {storage_integration_name};                 
            """)

    except Exception as e:
        logger.error(f"An error occured while creating and loading the stage: {e}")
        raise RuntimeError(f"Failed to create database {database_name}: {e}")

   

def create_json_file_format(database_name,schema_name,file_format_name):

    file_format_script = f"""
        CREATE FILE FORMAT IF NOT EXISTS {database_name}.{schema_name}.{file_format_name}
        TYPE = 'JSON'

        COMPRESSION = 'NONE'

        TRIM_SPACE = TRUE

        STRIP_OUTER_ARRAY = TRUE

        NULL_IF = ('', 'NULL')

        STRIP_NULL_VALUES = FALSE
    """
    with conn.cursor() as curr:
        try:
            curr.execute(file_format_script)
            logger.info("Successfully created Json file format")
        except Exception as e:
            logger.info(f"An error occured while creating a fileformat: {e}")
            raise RuntimeError(f"Failed to create FILE FORMAT {file_format_name}: {e}")

    
  
def create_table_restaurants():

    create_table_restaurant_script = """
        CREATE TABLE IF NOT EXISTS restaurants (
            restaurant_id INT NOT NULL,
            restaurant_name VARCHAR(50),
            PRIMARY KEY(restaurant_id));
    """
    with conn.cursor() as curr:
        try:
            curr.execute(create_table_restaurant_script)
            logger.info("Successfully created table: Restaurant")
        except Exception as e:
            logger.info(f"An error occured while creating table: Restaurant: {e}")
            raise RuntimeError(f"An error occured while creating table: Restaurant: {e}") 

def create_table_platforms():

    create_table_platform_script = """
        CREATE TABLE IF NOT EXISTS platforms (
            platform_id INT IDENTITY START 1 INCREMENT 1,
            platform_name VARCHAR(50),
            PRIMARY KEY(platform_id));
    """
    with conn.cursor() as curr:
        try:
            curr.execute(create_table_platform_script)
            logger.info("Successfully created table: Platform")
        except Exception as e:
            logger.info(f"An error occured while creating table: Platform: {e}")
            raise RuntimeError(f"An error occured while creating table: Platform: {e}")

def create_table_customers():

    create_customer_table_script = """
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INT PRIMARY KEY IDENTITY START 1 INCREMENT 1,
            customer_name VARCHAR(100) NOT NULL,
            customer_phone VARCHAR(50) NOT NULL,
            customer_email VARCHAR(50) NOT NULL);
    """
    with conn.cursor() as curr:
        try:
            curr.execute(create_customer_table_script)
            logger.info("Successfully created table: Customers")
        except Exception as e:
            logger.info(f"An error occured while creating table: Customers: {e}")
            raise RuntimeError(f"An error occured while creating table: Customers: {e}") 


def create_table_payments():

    create_table_payments_script = """
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
    with conn.cursor() as curr:
        try:
            curr.execute(create_table_payments_script)
            logger.info("Successfully created table: Payments")
        except Exception as e:
            logger.info(f"An error occured while creating table: Payments: {e}")
            raise RuntimeError(f"An error occured while creating table: Payments: {e}") 


def create_table_reservations():

    create_table_reservations_script = """
        CREATE TABLE IF NOT EXISTS reservations (
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
            payment INT REFERENCES payments(payment_id)
        
        )
       
    """
    with conn.cursor() as curr:
        try:
            curr.execute(create_table_reservations_script)
            logger.info("Successfully created table: Reservations")
        except Exception as e:
            logger.info(f"An error occured while creating table: Reservations: {e}")
            raise RuntimeError(f"An error occured while creating table: Reservations: {e}")

def insert_into_restaurant_platform_table():
    """
        One time load script
    """
    insert_into_restaurant = f"""
            INSERT INTO restaurants(restaurant_id, restaurant_name) 
            SELECT DISTINCT $1:restaurant_id::INT, $1:restaurant_name
            FROM @S3_STAGE_TEST/{date_today}
            (FILE_FORMAT => 'READ_RESERVATION_JSON')

        """

    insert_into_platform = f"""

        INSERT INTO platforms(platform_name)
        SELECT DISTINCT $1:platform
        FROM @s3_stage_test/{date_today}
        (FILE_FORMAT => 'READ_RESERVATION_JSON')

    """
    
    try:
        
        with conn.cursor() as curr:
            curr.execute(insert_into_restaurant)
            curr.execute(insert_into_platform)

    except Exception as e:
        logger.error(f"An error occured while inserting data into restaurant/platform table...: {e}")


def run_table_creation_scripts(database_name, schema_name):
    try:
        with conn.cursor() as curr:
            curr.execute(f"USE DATABASE {database_name}")
            curr.execute(f"USE SCHEMA {database_name}.{schema_name}")

        create_table_platforms()
        create_table_restaurants()
        create_table_payments()
        create_table_customers()
        create_table_reservations()

    except Exception as e:
        logger.error(f"An error occured while creating the tables: {e}")
        raise RuntimeError(f"An error occured while creating the tables: {e}") 


def run_default_insert_into_restaurant_platform_scripts():
    try:
        insert_into_restaurant_platform_table()
    except Exception as e:
        logger.error(f"An error occured while inserting into the default tables: {e}")
        raise RuntimeError("SQL error") from e
    

def select_table_creation_script(name, database_name, schema_name):
    with conn.cursor() as curr:
            curr.execute(f"USE DATABASE {database_name}")
            curr.execute(f"USE SCHEMA {database_name}.{schema_name}")
            if name == "CUSTOMERS":
                create_table_customers()
            elif name == "PAYMENTS":
                create_table_payments()
            elif name == "RESERVATIONS":
                create_table_reservations()
            elif name == "PLATFORMS":
                create_table_platforms()
            elif name == "RESTAURANTS":
                create_table_restaurants()
            else:
                raise ValueError("Invalid input value for table")