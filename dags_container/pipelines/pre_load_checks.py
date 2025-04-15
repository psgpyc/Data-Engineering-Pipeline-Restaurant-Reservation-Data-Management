from loader.pre_load_checks import run_pre_load_checks

from config.settings import DATABASE_NAME, SCHEMA_NAME, EXTERNAL_STAGE, STORAGE_INTEGRATION, FILE_FORMAT_NAME, TABLES, LOGGER

def pre_load_checks(process_success):
        
        """
            Executes pre-load checks to ensure required Snowflake objects 
            (e.g., tables, stages, file formats) exist before loading data.

            Parameters:
                process_success (dict): Output from the previous step indicating 
                                        success of the processing task.

            Returns:
                dict: Result of the pre-load check step, always returns {'success': True} for now.
        """
        logger = LOGGER

        logger.info("Starting pre-load checks for required Snowflake objects...")

        run_pre_load_checks(
                logger, 
                DATABASE_NAME,
                SCHEMA_NAME, 
                EXTERNAL_STAGE, 
                STORAGE_INTEGRATION, 
                FILE_FORMAT_NAME, 
                TABLES
        )

        logger.info("Pre-load checks completed successfully.")

        return {'success': True}