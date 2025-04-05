from faker import Faker
import random
import uuid
import json
from datetime import datetime, timedelta

fake = Faker()

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

def generate_bookings_file(restaurant_id, restaurant_name, platform, num_bookings=5000):
    bookings = [generate_booking(restaurant_id, restaurant_name, platform) for _ in range(num_bookings)]

    filename = f"restaurant_{restaurant_id}_bookings.json"
    with open(filename, "w") as f:
        json.dump(bookings, f, indent=2)

    print(f"✅ Generated {num_bookings} bookings for {restaurant_name} ({platform}) → {filename}")

# Example usage:
generate_bookings_file(restaurant_id=103, restaurant_name="Resz", platform="OpenTable", num_bookings=5000)