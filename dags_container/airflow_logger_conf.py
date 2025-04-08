"""
    Steps:
    -  Create a directory to store the config file e.g. ~/airflow/config

    -  Create file called ~/airflow/config/log_config.py with the contents of this file

    -  Update $AIRFLOW_HOME/airflow.cfg to contain:

       logging_config_class = log_config.LOGGING_CONFIG

"""
from copy import deepcopy
from datetime import datetime
from airflow.config_templates.airflow_local_settings import DEFAULT_LOGGING_CONFIG

LOGGING_CONFIG = deepcopy(DEFAULT_LOGGING_CONFIG)
TODAY = datetime.now().strftime('%Y:%m:%d')


LOGGING_CONFIG['formatters'].update({
    'custom': {
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    }
})

LOGGING_CONFIG['handlers'].update({
    'custom_write_to_file_handler': {

        'class': 'logging.FileHandler',
        'formatter': 'custom',
        'filename': f'/Users/psgpyc/Projects/ozzy/dags_container/logs/{TODAY}.log',
        'mode': 'a'
        }
})

LOGGING_CONFIG['loggers'].update({
    'custom_pipeline_logger': {
        'handlers': ['custom_write_to_file_handler'],
        'level': 'INFO',
        'propagate': False
    }
})

