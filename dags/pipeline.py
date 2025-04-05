import os
from datetime import datetime, timedelta
from airflow.decorators import dag, task

os.environ['NO_PROXY'] = '*'

default_args = {
    'owner': 'psgpyc',
    'retries': 3,
    'retry_delay': timedelta(minutes=2)
}


@dag(dag_id="reservation_data_daily_dag", 
     default_args=default_args, 
     start_date=datetime(2025, 4, 2), 
     schedule='30 8 * * *',   #runs at 8:30 AM daily.
     tags=['etl', 'reservation'],
     catchup=False)
def etl_process_reservation_data_daily():
    @task(task_id="extract-res-data", retries=3, retry_delay=timedelta(minutes=2), depends_on_past=False)
    def extract(**kwargs):
        print("hello form the task api")

        return {'data': 'sikka'}

    extract()

etl_process_reservation_data_daily()