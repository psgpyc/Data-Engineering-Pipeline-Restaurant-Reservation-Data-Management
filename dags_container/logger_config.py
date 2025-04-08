import logging
from datetime import datetime

def set_logger():
    today = datetime.now().strftime('%Y:%m:%d')
    logger = logging.getLogger(f'custom_pipeline_logger')


    file_handler = logging.FileHandler(f"/Users/psgpyc/Projects/ozzy/dags_container/logs/{today}.log", mode='a')
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger
