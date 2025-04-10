import logging
from snowflake_configs.establish_connection import get_connector
# from snowflake_configs.creation_snowflake import use_existing
from datetime import datetime

conn = get_connector()
curr = conn.cursor()

logger = logging.getLogger("custom_pipeline_logger")

date_today = datetime.now().strftime("%Y-%m-%d")

def insert_into_payment_table():
    payment_table = f"""
        INSERT INTO payments(payment_method, card_last_four, amount_paid, tip_amount, service_fee, total_amount)
        SELECT
            DISTINCT $1:payment:payment_method::STRING,
            $1:payment:card_last_four::INT,
            $1:payment:amount_paid::DECIMAL(10,2),
            $1:payment:tip_amount::DECIMAL(10,2),
            $1:payment:service_fee::DECIMAL(10,2),
            $1:payment:total_amount::DECIMAL(10,2)
        FROM @s3_stage_test/{date_today}
        (FILE_FORMAT => 'READ_RESERVATION_JSON')    
    """
    try:
        curr.execute(payment_table)
        inserted_rows = curr.rowcount
        logger.info(f"Successfully inserted {inserted_rows} rows into Payments Table")
    except Exception as e:
        logger.error(f"An error occured while trying to insert into payments table: {e}")
        raise RuntimeError("SQL error") from e
    

def insert_into_customer_table():

    customer_table = f"""
        INSERT INTO customers(customer_name, customer_phone, customer_email)
        SELECT DISTINCT 
            $1:customer_name::STRING,
            $1:customer_phone::STRING,
            $1:customer_email::STRING
        FROM @s3_stage_test/{date_today}
        (FILE_FORMAT => 'READ_RESERVATION_JSON') 
        WHERE
            ($1:customer_name::STRING, $1:customer_phone::STRING,  $1:customer_email::STRING)
        NOT IN
            (
                SELECT customer_name, customer_phone, customer_email FROM customers
            )     
    """
    try:
        curr.execute(customer_table)
        inserted_rows = curr.rowcount
        logger.info(f"Successfully inserted {inserted_rows} rows into Customers Table")

    except Exception as e:
        logger.error(f"An error occured when trying to insert into customers table")
        raise RuntimeError("SQL error") from e

def insert_into_reservation_table():

    reservation_table = f"""
        INSERT INTO reservation(reservation_id, status, reservation_date, party_size, special_request, created_at, updated_at)
        SELECT
            $1:reservation_id::STRING AS reservation_id,
            $1:status::STRING AS status,
            $1:date_time::DATETIME AS reservation_date,
            $1:party_size::INT AS party_size,
            $1:special_requests::TEXT AS special_requests,
            $1:created_at::DATETIME AS created_at,
            $1:updated_at::DATETIME AS updated_at
        FROM @s3_stage_test/{date_today}
        (FILE_FORMAT => 'READ_RESERVATION_JSON')
        WHERE $1:reservation_id::STRING 
        NOT IN
            (
                SELECT reservation_id FROM reservation
            )
    """
    
    try:
        curr.execute(reservation_table)
        inserted_rows = curr.rowcount
        logger.info(f"Successfully inserted {inserted_rows} rows into Reservation Table")
    except Exception as e:
        logger.error(f"An error occured while inserting data..:{e}")
        raise RuntimeError("SQL error") from e
  



def run_insert_statements():
    success = None
    try:
        curr.execute("USE ROLE accountadmin;")
        curr.execute("USE SCHEMA ozzy.base;")
        insert_into_payment_table()
        insert_into_customer_table()
        insert_into_reservation_table()
        success = True
        return  success
    except RuntimeError as e:
        logger.error("Insert statements failed.")