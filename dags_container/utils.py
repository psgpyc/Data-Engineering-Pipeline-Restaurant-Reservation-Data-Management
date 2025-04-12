from snowflake_configs.establish_connection import get_connector

conn = get_connector()


def database_exists(database_name: str):
    """
        Checks if a database exists in the Snowflake account.

        Parameters:
            database_name (str): Name of the database to check.

        Returns:
            bool: True if the database exists, False otherwise.
    """

    with conn.cursor() as curr:
        curr.execute(f"SHOW DATABASES LIKE '{database_name}'")
        result = curr.fetchall()
        return len(result) == 1
    



def schema_exists(database_name: str, schema_name: str):
    """
        Checks if a schema exists within a specified database.

        Parameters:
            database_name (str): Name of the database.
            schema_name (str): Name of the schema to check.

        Returns:
            bool: True if the schema exists, False otherwise.
    """
    with conn.cursor() as curr:
        curr.execute("USE ROLE accountadmin")
        curr.execute(f"""
            SELECT SCHEMA_NAME
            FROM {database_name}.INFORMATION_SCHEMA.SCHEMATA
            WHERE SCHEMA_NAME = '{schema_name}';
        """)
        result = curr.fetchall()
        return len(result) == 1
    


def stage_exists(database_name, stage_name):
    """
        Checks if a stage exists in a given database.

        Parameters:
            database_name (str): Name of the database.
            stage_name (str): Name of the stage to check.

        Returns:
            bool: True if the stage exists, False otherwise.
    """
    with conn.cursor() as curr:
        curr.execute("USE ROLE accountadmin")
        curr.execute(f"""
            SELECT STAGE_NAME
            FROM {database_name}.INFORMATION_SCHEMA.STAGES
            WHERE STAGE_NAME = '{stage_name}';
        """)
        result = curr.fetchall()
        return len(result) == 1


def check_privilege_in_storage_integration(integration_name='ozzy_pipeline_s3_access', role='SYSADMIN'):
    with conn.cursor() as curr:
        curr.execute(f"""
            SHOW GRANTS ON  INTEGRATION {integration_name};
        """)
        curr.execute(f"""
            SELECT 
                "grantee_name"
            FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()));
        """)
        current_roles_with_access_previliege = [roles[0] for roles in curr.fetchall()]
        if role not in current_roles_with_access_previliege:
            return False
        return True
            

def grant_usuage_access_to_storage_integration(integration_name='ozzy_pipeline_s3_access', role="SYSADMIN"):
    with conn.cursor() as curr:
        curr.execute("USE ROLE accountadmin;")
        curr.execute(f"""
            GRANT USAGE ON INTEGRATION {integration_name} TO ROLE {role};
        """)
        curr.execute(f"USE ROLE {role}")
        if len(curr.fetchall())  > 0:
            return True
        return False
        

def storage_integration_exists(integration_name):
    """
        Checks if a storage integration exists.

        Parameters:
            integration_name (str): Name of the storage integration to check.

        Returns:
            bool: True if the storage integration exists, False otherwise.
    """
    with conn.cursor() as curr:
        curr.execute(f"SHOW STORAGE INTEGRATIONS LIKE '{integration_name}'")
        result = curr.fetchall()
        return len(result) == 1


def file_format_exists(database_name: str, file_format_name: str):
    """
        Checks if a file format exists in a given database.

        Parameters:
            database_name (str): Name of the database.
            file_format_name (str): Name of the file format to check.

        Returns:
            bool: True if the file format exists, False otherwise.
    """
    with conn.cursor() as curr:
        curr.execute("USE ROLE accountadmin")
        curr.execute(f"""
            SELECT FILE_FORMAT_NAME
            FROM {database_name}.INFORMATION_SCHEMA.file_formats
            WHERE file_format_name = '{file_format_name}';
        """)
        result = curr.fetchall()
        return len(result) == 1
    

def tables_exists(database_name: str, schema_name: str):
    """
        Checks for the existence of tables in a given schema of a database.

        Parameters:
            database_name (str): Name of the database.
            schema_name (str): Name of the schema.

        Returns:
            list: List of table names if any exist, otherwise None.
            or
            bool: False if the file format doesnot exist
    """
    with conn.cursor() as curr:
        curr.execute("USE ROLE accountadmin")
        curr.execute(f"""
            SELECT TABLE_NAME
            FROM {database_name}.INFORMATION_SCHEMA.tables
            WHERE TABLE_SCHEMA = '{schema_name}' AND TABLE_TYPE='BASE TABLE';
        """)
        result = curr.fetchall()
        if len(result) != 0:
            return [each[0] for each in result]
        return None
    



