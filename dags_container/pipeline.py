import os
import logging
import requests
from pydantic import ValidationError
from datetime import datetime, timedelta
from airflow.decorators import dag, task

from validators import ReservationValidator

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
    @task(task_id="extract-res-data", retries=3, retry_delay=timedelta(minutes=2), depends_on_past=False)
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

    @task(task_id="transform-res-data", retries=3, retry_delay=timedelta(minutes=2), depends_on_past=True)
    def transform(data):
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
        print(data['validated'])

        
        return {'success': 'Successfully Done!!!'}

    agg_data = extract()
    response_data  = transform(data=agg_data)
    load(response_data)

etl_process_reservation_data_daily()