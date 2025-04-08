import os
import logging
import requests
from pydantic import ValidationError
from datetime import datetime, timedelta
from airflow.decorators import dag, task

from validators import ReservationValidator
from logger_config import set_logger

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
        logger.info('Fetching data...')
        res = requests.get("http://3.8.215.255/opentable/api/bookings/resx/prev")
        if res.status_code == 200:
            res_data = res.json()
            print(res_data)
            logger.info('data fetched successfully...')

            return {'data': res_data}
        else:
            return {'error': f'An error occured. Status Code:{res.status_code}'}

    @task(task_id="transform-res-data", retries=3, retry_delay=timedelta(minutes=2), depends_on_past=True)
    def transform(data):
        logger.info('data into transform pipe..')
        validated_reservation = []
        validation_error_reservation = []
        res = data
        logger.info("Data passed on to validators....")
        for each in res['data']:
            try:
                reservations = ReservationValidator(**each)
                validated_reservation.append(reservations)
            except ValidationError as e:
                validation_error.append(each)
                logging.error(f'An error occured: {e}')

        logger.info('Successfully validated data....')
        logger.info(f'Validated: {len(validated_reservation)}/{len(res["data"])}')
        logger.info(f'Error in validation:{len(validation_error_reservation)}')


    data_or_error = extract()
    transform(data=data_or_error)

etl_process_reservation_data_daily()