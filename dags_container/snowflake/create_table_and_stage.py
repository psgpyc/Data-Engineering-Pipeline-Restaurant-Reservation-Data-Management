from establish_connection import get_connector


curr = get_connector().cursor()
curr.execute("USE ROLE accountadmin")
curr.execute("CREATE DATABASE IF NOT EXISTS ozzy")
curr.execute("USE DATABASE ozzy")
curr.execute("CREATE SCHEMA IF NOT EXISTS ozzy.base")
curr.execute("USE SCHEMA base")


curr.execute("""
    CREATE OR REPLACE STAGE ozzy.base.s3_stage_test
    URL = 's3://booking-staging-bucket/'
    STORAGE_INTEGRATION = ozzy_pipeline_s3_access;
             
        
""")

curr.execute("LIST @s3_stage_test")