from establish_connection import get_connector

curr = get_connector().cursor()

def get_storage_integration():
    storage_name = "ozzy_pipeline_s3_access"
    create_storage_integration = f"""
        CREATE STORAGE INTEGRATION IF NOT EXISTS
            {storage_name}
        TYPE = EXTERNAL_STAGE
        STORAGE_PROVIDER = 'S3'
        STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::897729116490:role/read_restaurant_staging_bucket'
        ENABLED = TRUE
        STORAGE_ALLOWED_LOCATIONS = ('s3://booking-staging-bucket')
    """

    try:
        curr.execute("USE ROLE ACCOUNTADMIN;")
        curr.execute(create_storage_integration)
        result = curr.fetchall()

        return result, storage_name
    
    except Exception as e:
        print(f"An error occured {e}")


print(get_storage_integration())