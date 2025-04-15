import os
import json
import requests

from datetime import timedelta
from airflow.decorators import task
from config.settings import LOGGER, PLATFORMS, RESTAURANTS

logger = LOGGER

def extract(**kwargs):
    """
    Extracts booking data from various restaurant platforms for each restaurant.

    This function performs the following steps:
    1. Logs the start of the pipeline.
    2. Iterates over each platform defined in the PLATFORMS list.
    3. For each platform, it fetches the previous booking data for each restaurant from a mock API.
    4. Stores the response JSON (if the request is successful) in a nested dictionary.
    5. Logs success or error messages accordingly.
    6. Returns the aggregated booking data for all platforms and restaurants.

    Returns:
        dict: A nested dictionary of the structure:
              {
                  platform1: {
                      restaurant1: [...booking data...],
                      restaurant2: [...booking data...],
                      ...
                  },
                  platform2: {
                      ...
                  },
                  ...
              }
    """
    print('sikka')
    logger.info("Pipeline Initiated....")
        
    # Dictionary to store all aggregated booking data
    agg_data = {}

    # Iterate through each booking platform
    logger.info('Data Fetching Started....')
    for platform in PLATFORMS:
        agg_data[platform] = {}

        # Iterate through each restaurant for the given platform
        for restaurant in RESTAURANTS:
            try:
                response = requests.get(f"http://3.8.215.255/{platform}/api/bookings/{restaurant}/prev")
                if response.status_code == 200:
                    agg_data[platform][restaurant] = response.json()
                    logger.info(f'data fetched successfully for {platform}-{restaurant}')
                else:
                    logger.error(f'Failed to fetch data for {platform}-{restaurant}. '
                                    f'Status Code: {response.status_code}')
                    
            except requests.exceptions.RequestException as e:
                logger.error(f'Request failed for {platform}-{restaurant}: {str(e)}')

    logger.info("Data Fetching ended....")
    return agg_data   
