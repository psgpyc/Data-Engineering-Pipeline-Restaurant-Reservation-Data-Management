from config.settings import DATABASE_NAME, SCHEMA_NAME, EXTERNAL_STAGE, LOGGER
from snowflakecore.sql.create_update_script import run_insert_statements, run_create_view_statements, run_update_reservation_table_statements


DATABASE_NAME = DATABASE_NAME
SCHEMA_NAME = SCHEMA_NAME
EXTERNAL_STAGE = EXTERNAL_STAGE

logger = LOGGER


def load(load_success: dict) -> None:
    """
    Executes data loading tasks after successful pre-load checks.
    This includes inserting data into Snowflake tables, creating views,
    and updating the reservation table with the latest data.

    Parameters:
        load_success (dict): Output from the previous task indicating 
                             that pre-load checks passed successfully.

    Returns:
        None
    """

    logger.info("Starting data load operations into Snowflake...")

    success_insert = run_insert_statements(
        database_name=DATABASE_NAME,
        schema_name=SCHEMA_NAME,
        stage_name=EXTERNAL_STAGE
    )

    success_create_view = run_create_view_statements(
        database_name=DATABASE_NAME,
        schema_name=SCHEMA_NAME,
        stage_name=EXTERNAL_STAGE
    )

    success_update_reservation_table = run_update_reservation_table_statements(
        database_name=DATABASE_NAME,
        schema_name=SCHEMA_NAME
    )

    if success_insert:
        logger.info("Data insertion completed.")

    if success_create_view:
        logger.info("View creation completed.")

    if success_update_reservation_table:
        logger.info("Reservation table update completed.")

    logger.info("Data load pipeline completed successfully.")
