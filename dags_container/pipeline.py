import os
from airflow.decorators import dag, task
from datetime import datetime, timedelta
from pipelines import extract, validate, process, pre_load_checks,load

os.environ['NO_PROXY'] = '*'

default_args = {
    'owner': 'psgpyc',
    'retries': 3,
    'retry_delay': timedelta(minutes=2)
}

@dag(dag_id="data_daily_pipeline", 
     default_args=default_args, 
     start_date=datetime(2025, 4, 2), 
     schedule='30 8 * * *',   #runs at 8:30 AM daily.
     tags=['etl', 'reservation'],
     catchup=False)
def etl_process_reservation_data_daily():
    
    @task(task_id="extract-res-data", retries=3, retry_delay=timedelta(minutes=2))
    def run_extract(**kwargs):
        return extract.extract()
    
    @task(task_id="validate-res-data", retries=3, retry_delay=timedelta(minutes=2))
    def run_validate(response):
        return validate.validate(response)
    
    @task(task_id="load_data", retries=3, retry_delay=timedelta(minutes=2))
    def run_process(validated_data):
        return process.process(validated_data)
    
    @task(task_id="pre_load_checks")
    def run_pre_load_checks(process_success):
        return pre_load_checks.pre_load_checks(process_success)
    
    @task(task_id="transform_data", retries=3, retry_delay=timedelta(minutes=2))
    def run_load(load_success):
        return load.load(load_success)
    

    agg_data = run_extract()
    response_data  = run_validate(response=agg_data)
    load_success = run_process(validated_data=response_data)
    pre_load_check_success = run_pre_load_checks(process_success=load_success)
    run_load(pre_load_check_success)


etl_process_reservation_data_daily()