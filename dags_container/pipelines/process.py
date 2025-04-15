import boto3
import json
from typing import Dict, Any
from datetime import datetime
from botocore.exceptions import ClientError

from config.settings import LOGGER, STAGE_BUCKET_NAME, DATE_FORMAT

logger = LOGGER

BUCKET_NAME = STAGE_BUCKET_NAME

DATE_FORMAT = DATE_FORMAT


def process(validated_data: Dict[str, Any]) -> Dict[str, bool]:
        """
            Uploads validated booking data to an S3 staging bucket in JSON format.

            Parameters:
                validated_data (dict): A dictionary containing booking data that has been validated.
                                    Must include the key 'validated'.

            Returns:
                dict: A dictionary indicating the success of the operation, e.g., {'success': True}.
        """
        # Ensure 'validated' key exists
        if 'validated' not in validated_data:
            logger.error("Missing 'validated' key in input data.")
            return {'success': False}

        # Convert data to formatted JSON string
        data_json = json.dumps(validated_data['validated'], indent=2)

        # Generate S3 object key with current date
        object_key = f"{datetime.now().strftime(DATE_FORMAT)}/processed.json"

        # Initialize S3 client
        s3_client = boto3.client('s3')

        try:
            # Upload the object to S3
            s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=object_key,
                Body=data_json,
                ContentType="application/json"
            )
            logger.info(f"Successfully uploaded processed file to s3://{BUCKET_NAME}/{object_key}")
            return {'success': True}

        except ClientError as e:
            logger.error(f"Error uploading processed file to {BUCKET_NAME}: {e}")
            return {'success': False}