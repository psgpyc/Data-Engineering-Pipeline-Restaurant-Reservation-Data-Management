from pydantic import BaseModel, Field, EmailStr, constr
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class Payments(BaseModel):
    """
        Contains detailed payment information related to a reservation.
        Not currently used in ReservationValidator but available for extension.
    """
    payment_method: str
    card_last_four: str
    amount_paid: Decimal
    tip_amount: Decimal
    service_fee: Decimal
    total_amount: Decimal

class ReservationValidator(BaseModel):
    """
        Validates complete reservation data including customer details, booking information,
        and associated experiences.
    """
    reservation_id: UUID
    restaurant_id: str
    restaurant_name: str
    platform: str
    status: str
    date_time: datetime
    party_size:int = Field(..., gt=0, lt=50)
    customer_name: str
    customer_phone: str
    customer_email: EmailStr
    special_requests: str | None
    created_at: datetime
    updated_at: datetime
    payment: Payments

