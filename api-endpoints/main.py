import json
import asyncio
import boto3
import logging
import datetime
from dateutil.tz import tzutc
from botocore.exceptions import ClientError
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from pathlib import Path


s3c = boto3.client('s3')

def get_bucket_keys(bucket_name='booking-raw-bucket', extraction_date=datetime.datetime.now().date()):
    try:
        response = s3c.list_objects_v2(Bucket=bucket_name)
        if 'Contents' not in response:
            print('No objects found. Bucket might be empty...')
        else:
            contents = [ content['Key'] for content in response['Contents'] if content['LastModified'].date() == extraction_date]
            return contents
            # return [content['Key'] for content in contents]
    except ClientError as e:
        logging.error(e)


@asynccontextmanager
async def lifespan(app: FastAPI):

    print(get_bucket_keys())

    yield


app = FastAPI(lifespan=lifespan)



def generate_keys(extraction_date, platform, res_name):
    obj_key = f"{extraction_date}/{platform}/{res_name}_{extraction_date}.json"
    return obj_key


@app.get("/{platform}/api/bookings/{restaurant_id}/{date_today}")
def get_booking(platform: str, restaurant_id: str, date_today:str):
    if date_today == 'prev':
        date_obj = datetime.datetime.now().date()
        date_today_str = datetime.datetime.now().strftime('%Y-%m-%d')

        todays_booking_items_keys = get_bucket_keys(extraction_date=date_obj)

        to_get_object_key = generate_keys(date_today_str, platform=platform, res_name=restaurant_id)

        if to_get_object_key in todays_booking_items_keys:
            response = s3c.get_object(Bucket='booking-raw-bucket', Key=to_get_object_key)
            
            content = response['Body'].read().decode('utf-8')
            
            data = json.loads(content)
            
            if not data:
                raise HTTPException(status_code=404, detail="Restaurant not found")
            
            return JSONResponse(content=data)
        
        else:
            return JSONResponse(content={'error': 'Key not found in the current object llist'})
    else:
        return JSONResponse(content={'error': 'Invalid api invocation path'})

    




