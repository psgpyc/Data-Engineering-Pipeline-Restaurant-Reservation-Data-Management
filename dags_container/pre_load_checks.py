from snowflake_configs.establish_connection import get_connector

from snowflake_configs.creation import (
    create_database, 
    create_schema, 
    create_external_stage, 
    create_json_file_format, 
    run_table_creation_scripts , 
    select_table_creation_script )

from utils import (
    database_exists, 
    schema_exists, 
    stage_exists, 
    file_format_exists, 
    storage_integration_exists, 
    tables_exists, 
    check_privilege_in_storage_integration,
    grant_usuage_access_to_storage_integration)


conn = get_connector()

def run_pre_load_checks(logger, DATABASE_NAME, SCHEMA_NAME, EXTERNAL_STAGE, STORAGE_INTEGRATION, FILE_FORMAT_NAME, TABLES):

    exists = database_exists(database_name=DATABASE_NAME)

    if not exists:
        create_database(database_name=DATABASE_NAME)
        logger.info(f"Successfully created database:{DATABASE_NAME}")
    else:
        logger.info(f"Database {DATABASE_NAME} exists.")

    exists = schema_exists(database_name=DATABASE_NAME, schema_name=SCHEMA_NAME)
    if not exists:
        create_schema(database_name=DATABASE_NAME, database_schema=SCHEMA_NAME)
        logger.info(f"Successfully created schema: {SCHEMA_NAME}")
    else:
        logger.info(f"Schema {SCHEMA_NAME} exists.")

    exists = storage_integration_exists(integration_name=STORAGE_INTEGRATION)
    if not exists:
        logger.error("Unable to locate storage integration. Please ensure storage inregration exists.")
        raise ValueError("Unable to proceed. Storage integration doesnot exists....")
    else:
        logger.info(f"Storage Integration {STORAGE_INTEGRATION} exists.")


    exists = stage_exists(database_name=DATABASE_NAME, stage_name=EXTERNAL_STAGE)
    if not exists:
        if not check_privilege_in_storage_integration(integration_name=STORAGE_INTEGRATION):
            grant_usuage_access_to_storage_integration(integration_name=STORAGE_INTEGRATION)
        create_external_stage(stage_name=EXTERNAL_STAGE, database_name=DATABASE_NAME, schema_name=SCHEMA_NAME, storage_integration_name=STORAGE_INTEGRATION)
        logger.info(f"Successfully created external stage: {EXTERNAL_STAGE} with storage integration: {STORAGE_INTEGRATION}")
    else:
        logger.info(f"External Stage: {EXTERNAL_STAGE} exists.")


    exists = file_format_exists(database_name=DATABASE_NAME, file_format_name=FILE_FORMAT_NAME)
    if not exists:
        create_json_file_format(database_name=DATABASE_NAME, schema_name=SCHEMA_NAME, file_format_name=FILE_FORMAT_NAME)
        logger.info(f"Successfully created file format: {FILE_FORMAT_NAME} ")
    else:
        logger.info(f"FILE FORMAT: {FILE_FORMAT_NAME} exists.")

    existing_table_names = tables_exists(database_name=DATABASE_NAME, schema_name=SCHEMA_NAME)
    print(existing_table_names)
    if existing_table_names is not None: 
        for each in TABLES:
            if each not in existing_table_names:
                logger.info(f"Table {each} does not exists. Entering creation.")
                select_table_creation_script(name=each, database_name=DATABASE_NAME, schema_name=SCHEMA_NAME) 
            else:
                logger.info(f"Table {each} exists")

    if existing_table_names is None:
        run_table_creation_scripts(database_name=DATABASE_NAME, schema_name=SCHEMA_NAME)
