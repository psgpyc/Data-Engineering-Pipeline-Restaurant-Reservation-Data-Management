import os
import boto3
from botocore.exceptions import ClientError
import json
import logging
import requests
from pydantic import ValidationError
from datetime import datetime, timedelta
from airflow.decorators import dag, task
from validators import ReservationValidator
from sql_script import run_insert_statements, run_create_view_statements, run_update_reservation_table_statements
from pre_load_checks import run_pre_load_checks

os.environ['NO_PROXY'] = '*'

default_args = {
    'owner': 'psgpyc',
    'retries': 3,
    'retry_delay': timedelta(minutes=2)
}

logger = logging.getLogger(f'custom_pipeline_logger')

@dag(dag_id="reservation_data_daily_dag", 
     default_args=default_args, 
     start_date=datetime(2025, 4, 2), 
     schedule='30 8 * * *',   #runs at 8:30 AM daily.
     tags=['etl', 'reservation'],
     catchup=False)
def etl_process_reservation_data_daily():

    
    @task(task_id="extract-res-data", retries=3, retry_delay=timedelta(minutes=2))
    def extract(**kwargs):
        
        logger.info("                                         ")
        logger.info("Pipeline Initiated....")

        platforms = ['opentable','fork']
        restaurants = ['resx', 'resy', 'resz']

        agg_data = {}

        logger.info('Data Fetching Started....')
        for platform in platforms:
            agg_data[platform] = {}
            for restaurant in restaurants:
                response = requests.get(f"http://3.8.215.255/{platform}/api/bookings/{restaurant}/prev")
                if response.status_code == 200:
                    agg_data[platform][restaurant] = response.json()
                    logger.info(f'data fetched successfully for {platform}-{restaurant}')
                else:
                    logger.error(f'An error occured. Status Code:{response.status_code}')
        logger.info("Data Fetching ended....")
        return agg_data

    @task(task_id="validate-res-data", retries=3, retry_delay=timedelta(minutes=2))
    def validate(data):
        logger.info('\n data entered transform pipe..')
        validated_reservation = []
        validation_error_reservation = []
        res = data
        logger.info("Data passed on to validators....")
        for platform in res:
            for restaurant in data[platform]:
                for reservation in data[platform][restaurant]:
                    try:
                        reservations = ReservationValidator(**reservation)
                        validated_reservation.append(reservations.model_dump(mode='json'))
                    except ValidationError as e:
                        validation_error_reservation.append(reservation)
                        logging.error(f'An error occured: {e}')

        print(validated_reservation)
        logger.info(f'Validated: {len(validated_reservation)}')
        logger.info(f'Validated: {len(validation_error_reservation)}')

        if len(validation_error_reservation)  != 0:
            logger.error(f'Error in validation:{len(validation_error_reservation)}')

        return {
            'validated': validated_reservation,
            'error': validation_error_reservation
        }
    
    @task(task_id="load_data", retries=3, retry_delay=timedelta(minutes=2))
    def process(validated_data):
        data = validated_data
        data_json = json.dumps(data['validated'], indent=2)
        s3c = boto3.client('s3')
        bucket_name = "booking-staging-bucket"
        object_key = f"{datetime.now().date()}/processed.json"
        try:
            s3c.put_object(Bucket=bucket_name, Key=object_key, Body=data_json, ContentType="application/json")
            logger.info("Successfully loaded into the staging bucket.")

        except ClientError as e:
            logger.error(f"An error has occured while loading processed file into {bucket_name}: {e}")
        
        return {'success': True}
    
    @task(task_id="pre_load_checks")
    def pre_load_checks(process_success):

        DATABASE_NAME = "RRANALYTICS"
        SCHEMA_NAME = "RESERVATIONS"
        EXTERNAL_STAGE = "RESERVATION_LAKE"
        STORAGE_INTEGRATION = "ozzy_pipeline_s3_access"
        FILE_FORMAT_NAME = "READ_RESERVATION_JSON"
        TABLES = ["RESTAURANTS", "PLATFORMS", "CUSTOMERS", "PAYMENTS", "RESERVATIONS"]

        run_pre_load_checks(logger, DATABASE_NAME, SCHEMA_NAME, EXTERNAL_STAGE, STORAGE_INTEGRATION, FILE_FORMAT_NAME, TABLES)

        return {'success': True}
    
    @task(task_id="transform_data", retries=3, retry_delay=timedelta(minutes=2))
    def load(load_success):

        DATABASE_NAME = "RRANALYTICS"
        SCHEMA_NAME = "RESERVATIONS"
        EXTERNAL_STAGE = "RESERVATION_LAKE"
        
        logger.info("Insertion started....")
        success_insert = run_insert_statements(database_name=DATABASE_NAME, schema_name=SCHEMA_NAME, stage_name=EXTERNAL_STAGE)
        success_create_view = run_create_view_statements(database_name=DATABASE_NAME, schema_name=SCHEMA_NAME, stage_name=EXTERNAL_STAGE)
        success_update_reservation_table = run_update_reservation_table_statements(database_name=DATABASE_NAME, schema_name=SCHEMA_NAME)
        if success_insert:
            logger.info("Insertion Completed....")

        if success_create_view:
            logger.info("Create view Completed...")   
            
        if success_update_reservation_table:
            logger.info("Update reservation statement Completed")   
            
        logger.info("Pipeline Ended..")

    agg_data = extract()
    response_data  = validate(data=agg_data)
    load_success = process(response_data)
    pre_load_check_success = pre_load_checks(load_success)
    load(pre_load_check_success)


etl_process_reservation_data_daily()