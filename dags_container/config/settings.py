import logging
from datetime import datetime, timedelta

DATABASE_NAME = "RRANALYTICS"

SCHEMA_NAME = "RESERVATIONS"

EXTERNAL_STAGE = "RESERVATION_LAKE"

STORAGE_INTEGRATION = "ozzy_pipeline_s3_access"

FILE_FORMAT_NAME = "READ_RESERVATION_JSON"

TABLES = ["RESTAURANTS", "PLATFORMS", "CUSTOMERS", "PAYMENTS", "RESERVATIONS"]

LOGGER = logging.getLogger(f'custom_pipeline_logger')

DEFAULT_ARGS = {
    'owner': 'psgpyc',
    'retries': 3,
    'retry_delay': timedelta(minutes=2)
}

PLATFORMS = ['opentable','fork']

RESTAURANTS =  ['resx', 'resy', 'resz']

STAGE_BUCKET_NAME = "booking-staging-bucket"

DATE_FORMAT = "%Y-%m-%d"
