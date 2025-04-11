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
  

def create_payment_id_view():
    create_payment_view = f"""
        CREATE OR REPLACE VIEW payment_joined AS (
        SELECT
            p.payment_id, st.reservation_id
        FROM 
            payments AS p
        INNER JOIN 
            (
            SELECT 
                $1:reservation_id AS reservation_id,
                $1:payment:payment_method::STRING AS payment_method,
                $1:payment:card_last_four::INT AS card_last_four,
                $1:payment:amount_paid::DECIMAL(10,2) AS amount_paid,
                $1:payment:tip_amount::DECIMAL(10,2) AS tip_amount,
                $1:payment:service_fee::DECIMAL(10,2) AS service_fee,
                $1:payment:total_amount::DECIMAL(10,2) AS total_amount 
            FROM @s3_stage_test/{date_today}
            (FILE_FORMAT => 'READ_RESERVATION_JSON')
            
            ) AS st
        ON
        p.card_last_four = st.card_last_four AND p.amount_paid = st.amount_paid AND p.total_amount = st.total_amount);
        """

    try:
        curr.execute(create_payment_view)
        logger.info("Successfully created [payment_joined] view")
    except Exception as e:
        logger.error(f"An error occured while creating payment view..:{e}")
        raise RuntimeError("SQL error") from e
  

def create_customer_id_view():
    create_customer_view = f"""
        CREATE OR REPLACE VIEW customer_joined AS (
            SELECT
                c.customer_id, st.reservation_id
            FROM 
                customers AS c
            INNER JOIN 
                (
                SELECT 
                    $1:reservation_id AS reservation_id,
                    $1:customer_name::STRING AS customer_name, 
                    $1:customer_phone::STRING AS customer_phone,
                    $1:customer_email::STRING AS customer_email
                FROM @s3_stage_test/{date_today}
                (FILE_FORMAT => 'READ_RESERVATION_JSON')
                
                ) AS st
            ON
            c.customer_name = st.customer_name AND
            c.customer_email = st.customer_email AND
            c.customer_phone = st.customer_phone)
    """
    try:
        curr.execute(create_customer_view)
        logger.info("Successfully created [customer_joined] view")
    except Exception as e:
        logger.error(f"An error occured while creating customer view..:{e}")
        raise RuntimeError("SQL error") from e

def create_restaurant_id_view():
    create_restaurant_view = f"""
        CREATE OR REPLACE VIEW restaurant_joined AS (
            SELECT
                r.restaurant_id, st.reservation_id
            FROM 
                restaurants AS r
            INNER JOIN 
                (
                SELECT 
                    $1:reservation_id AS reservation_id,
                    $1:restaurant_id::INT AS restairant_id, 
                    $1:restaurant_name::STRING AS restaurant_name
                FROM @s3_stage_test/{date_today}
                (FILE_FORMAT => 'READ_RESERVATION_JSON')
                
                ) AS st
            ON
            r.restaurant_id = st.restairant_id AND
            r.restaurant_name = st.restaurant_name )
    """


    try:
        curr.execute(create_restaurant_view)
        logger.info("Successfully created [restaurant_joined] view")
    except Exception as e:
        logger.error(f"An error occured while creating restaurant view..:{e}")
        raise RuntimeError("SQL error") from e


def create_platform_id_view():
    create_platform_view = f"""
        CREATE OR REPLACE VIEW platform_joined AS (
            SELECT
                p.platform_id, st.reservation_id
            FROM 
                platforms AS p
            INNER JOIN 
                (
                SELECT 
                    $1:reservation_id AS reservation_id,
                    $1:platform::STRING AS platform_name, 
                FROM @s3_stage_test/{date_today}
                (FILE_FORMAT => 'READ_RESERVATION_JSON')
                
                ) AS st
            ON
            p.platform_name = st.platform_name)
    """
    try:
        curr.execute(create_platform_view)
        logger.info("Successfully created [platform_joined] view")
    except Exception as e:
        logger.error(f"An error occured while creating platform view..:{e}")
        raise RuntimeError("SQL error") from e


def update_platform_id():
    update_platform_id_script = f"""
        UPDATE reservation r
        SET 
            r.platform = pv.platform_id::INT 
        FROM platform_joined AS pv
        WHERE
        r.reservation_id = pv.reservation_id
    """

    try:
        curr.execute(update_platform_id_script)
        logger.info("Successfully updated reservation table platform fkey with data")
    except Exception as e:
        logger.error(f"An error occured while updating reservation table with platform id..:{e}")
        raise RuntimeError("SQL error") from e
    
def update_restaurant_id():
    update_restaurant_id_script = """
        UPDATE reservation r
        SET 
            r.restaurant_id = rj.restaurant_id::INT
            
        FROM restaurant_joined AS rj
        WHERE
        r.reservation_id = rj.reservation_id
    """
    try:
        curr.execute(update_restaurant_id_script)
        logger.info("Successfully updated reservation table restaurant_id fkey with data")
    except Exception as e:
        logger.error(f"An error occured while updating reservation table with restaurant id..:{e}")
        raise RuntimeError("SQL error") from e


def update_customer_id():
    update_customer_id_script = """
        UPDATE reservation r
        SET 
            r.customer_id = cj.customer_id::INT
            
        FROM customer_joined AS cj
        WHERE
        r.reservation_id = cj.reservation_id::STRING
    """
    try:
        curr.execute(update_customer_id_script)
        logger.info("Successfully updated reservation table customer_id fkey with data")
    except Exception as e:
        logger.error(f"An error occured while updating reservation table with customer id..:{e}")
        raise RuntimeError("SQL error") from e
    
def update_payment_id():
    update_payment_id_script = """
        UPDATE reservation r
            SET 
                r.payment = pj.payment_id::INT 
            FROM payment_joined AS pj
            WHERE
            r.reservation_id = pj.reservation_id
    """

    try:
        curr.execute(update_payment_id_script)
        logger.info("Successfully updated reservation table payment_id fkey with data")
    except Exception as e:
        logger.error(f"An error occured while updating reservation table with payment id..:{e}")
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


def run_create_view_statements():
    success = None
    try:
        curr.execute("USE ROLE accountadmin;")
        curr.execute("USE SCHEMA ozzy.base;")
        create_payment_id_view()
        create_platform_id_view()
        create_restaurant_id_view()
        create_customer_id_view()
        success = True
        return success
    except RuntimeError as e:
        logger.error("Create View Statement Failed..")
        

def run_update_reservation_table_statements():
    success = None
    try:
        curr.execute("USE ROLE accountadmin;")
        curr.execute("USE SCHEMA ozzy.base;")
        update_payment_id()
        update_platform_id()
        update_restaurant_id()
        update_customer_id()
        success = True
        return success
    except RuntimeError as e:
        logger.error("Update from View Statement Failed..")
        