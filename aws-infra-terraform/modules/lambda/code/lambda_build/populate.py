import boto3
import random
import uuid
import json
import logging
from pathlib import Path
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

ROOT_DIR = Path(__file__).parent

DATA_DIR = ROOT_DIR / 'data'

def generate_booking(restaurant_id, restaurant_name, platform):
    reservation_id = str(uuid.uuid4())
    created_at = fake.date_time_between(start_date='-60d', end_date='-2d')
    updated_at = created_at + timedelta(days=random.randint(0, 5))
    reservation_time = fake.date_time_between(start_date='-1d', end_date='+30d')

    experience = {
        "name": random.choice(["Valentine’s Day Dinner", "Chef's Tasting", "Vegan Feast", "Set Menu", "Happy Dinner"]),
        "description": fake.sentence(nb_words=10),
        "prepaid": random.choice([True, False]),
        "price": round(random.uniform(30, 150), 2),
        "currency": "GBP"
    }

    tip = round(random.uniform(0, 20), 2)
    service_fee = round(random.uniform(0, 10), 2)
    total = experience["price"] + tip + service_fee

    booking = {
        "reservation_id": reservation_id,
        "restaurant_id": restaurant_id,
        "restaurant_name": restaurant_name,
        "platform": platform,
        "status": random.choice(["confirmed", "cancelled", "pending"]),
        "date_time": reservation_time.isoformat(),
        "party_size": random.randint(1, 8),
        "customer_name": fake.name(),
        "customer_phone": fake.phone_number(),
        "customer_email": fake.email(),
        "special_requests": random.choice(["", fake.sentence(nb_words=5)]),
        "created_at": created_at.isoformat(),
        "updated_at": updated_at.isoformat(),

        "experience": experience,

        "payment": {
            "payment_method": "card",
            "card_last_four": str(random.randint(1000, 9999)),
            "amount_paid": experience["price"],
            "tip_amount": tip,
            "service_fee": service_fee,
            "total_amount": total
        }
    }

    return booking

def generate_bookings_file(restaurant_id, restaurant_name, platform, num_bookings=100, save_local=False):

    bookings = [generate_booking(restaurant_id, restaurant_name, platform) for _ in range(num_bookings)]

    filename = f"{restaurant_name.lower()}_{datetime.now().date()}.json"
    
    if save_local:

        DAILY_DIR = DATA_DIR / str(datetime.now().date()) / platform

        if not DAILY_DIR.exists():
            DAILY_DIR.mkdir(parents=True)

        with open(DAILY_DIR / filename, "w") as f:
            json.dump(bookings, f, indent=2)

        print(f"✅ Generated {num_bookings} bookings for {restaurant_name} ({platform}) → {filename}")

    return bookings, filename


def lambda_handler(event, context):

    restaurants = [
        {'id': '101', 'name': 'resx'},
        {'id': '102', 'name': 'resy'},
        {'id': '103', 'name': 'resz'}
    ]

    platforms = ['opentable', 'fork']


    for platform in platforms:
        for restaurant in restaurants:
            booking_data, filename = generate_bookings_file(restaurant_id=restaurant['id'], restaurant_name=restaurant['name'], platform=platform, num_bookings=5000)

            json_data = json.dumps(booking_data, indent=2)


            s3c = boto3.client('s3')
            bucket_name = 'booking-raw-bucket'
            object_key = f"{datetime.now().date()}/{platform}/{filename}"


            try:
                s3c.put_object(Bucket=bucket_name, Key=object_key , Body=json_data, ContentType="application/json")
                print(f'Successfully generated and loaded data for {restaurant['name']} // {platform}')


            except Exception as e:
                logging.error(e)
                
    return {
        "statusCode": 200,
        "body": json.dumps("Bookings generated and uploaded to S3")
    }

