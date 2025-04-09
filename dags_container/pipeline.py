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
from snowflake_configs.creation_snowflake import insert_into_restaurant_platform_table

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
    def load(validated_data):
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
        
        return {'success': 'Successfully Done!!!'}
    

    @task(task_id="transform_data", retries=3, retry_delay=timedelta(minutes=2))
    def transform():
        logging.info("Inserting into restaurant platform table......")
        insert_into_restaurant_platform_table()


    # agg_data = extract()
    # response_data  = validate(data=agg_data)
    # load(response_data)
    transform()

etl_process_reservation_data_daily()